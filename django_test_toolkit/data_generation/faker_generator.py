import random

from django.conf import settings
from django.db.models import fields
from factory import django, Faker, base
from factory.django import DjangoOptions

from django_test_toolkit.data_generation.config import DEFAULT_FIELD_TO_FAKER_CONFIG
from django_test_toolkit.data_generation.constants import (
    DEFAULT_VALUE_FACTOR,
    FIELD_EXTRA_KWARGS,
    FIELD_PROCESSING_FUNC,
    FIELD_TO_FAKER_CONFIG,
    DEFAULT_RETRY_TOLERANCE,
    FIELD_PROVIDER,
    FIELDS,
    UNIQUE_FIELD_DUPLICATE_RETRY_TOLERANCE,
    USER_FIELD_PROVIDER,
    FAKER_LOCALE,
    DEFAULT_DEFAULT_VALUE_FACTOR,
)


class FakerGenerator(Faker):
    def generate(self, extra_kwargs, locale=None):
        """直接基于faker配置获得生成数据"""
        # 旧版本兼容
        try:
            generated_data = super().generate(extra_kwargs)
        except AttributeError:
            faker = self._get_faker(locale or self._defaults.get("locale"))
            generated_data = faker.format(self.provider, **extra_kwargs)
        return generated_data


class DjangoModelFakerOptions(DjangoOptions):
    def _build_default_options(self):
        field_to_faker_config = getattr(self.factory, "field_to_faker_config", None) or getattr(
            settings, "TEST_TOOLKIT_FAKER_CONFIG", DEFAULT_FIELD_TO_FAKER_CONFIG
        )
        return super()._build_default_options() + [
            base.OptionDefault(FIELD_TO_FAKER_CONFIG, field_to_faker_config, inherit=True,),
        ]


class DjangoModelFakerFactory(django.DjangoModelFactory):
    _options_class = DjangoModelFakerOptions

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        faker_generated_data = cls._generate_model_field_data(model_class, *args, **kwargs)
        return super()._create(model_class, *args, **kwargs, **faker_generated_data)

    @classmethod
    def _generate_model_field_data(cls, model_class, *args, **kwargs):
        """模型中各个字段生成数据"""
        fields = model_class._meta.fields
        faker_generated_data = {}
        faker_config = cls._meta.field_to_faker_config
        tolerance = int(faker_config.get(UNIQUE_FIELD_DUPLICATE_RETRY_TOLERANCE, DEFAULT_RETRY_TOLERANCE))
        fields_faker_config = faker_config.get(FIELDS, {})
        for field in fields:
            # 如果Factory中指定字段赋值方式，则不进行生成
            if field.name in kwargs:
                continue
            field_faker_config = fields_faker_config.get(type(field).__name__)
            if field_faker_config:
                value, is_generated = cls._generate_default_and_choices_value(field=field)
                if is_generated:
                    faker_generated_data[field.name] = value
                    continue
                faker_data, faker_generator, extra_kwargs = cls._generate_fake_data(field_faker_config, field)
                faker_generated_data[field.name] = cls._check_and_retry_for_unique_field(
                    model_class,
                    field,
                    tolerance,
                    first_generated_value=faker_data,
                    generate_func=faker_generator.generate,
                    func_kwargs={"extra_kwargs": extra_kwargs},
                )

        return faker_generated_data

    @staticmethod
    def _generate_fake_data(field_faker_config, field):
        """根据字段配置生成数据"""
        extra_kwargs = field_faker_config.get(FIELD_EXTRA_KWARGS, {})
        if FIELD_PROCESSING_FUNC in field_faker_config:
            extra_kwargs_generator = field_faker_config[FIELD_PROCESSING_FUNC]
            extra_kwargs.update(extra_kwargs_generator(field) or {})
        faker_generator = FakerGenerator(field_faker_config[FIELD_PROVIDER])
        faker_locale = field_faker_config.get(FAKER_LOCALE)
        if USER_FIELD_PROVIDER in field_faker_config:
            faker_generator.add_provider(field_faker_config[USER_FIELD_PROVIDER], locale=faker_locale)
        faker_data = faker_generator.generate(extra_kwargs, locale=faker_locale)
        return faker_data, faker_generator, extra_kwargs

    @classmethod
    def _check_and_retry_for_unique_field(
        cls, model_class, field, tolerance, first_generated_value, generate_func, func_kwargs
    ):
        """检查字段是否符合唯一约束，如果不符合则重试"""
        value = first_generated_value
        if field.unique:
            existing_values = cls._get_field_existing_values(model_class, field.name)
            for _ in range(tolerance):
                if value not in existing_values:
                    break
                value = generate_func(**func_kwargs)
        return value

    @classmethod
    def _get_field_existing_values(cls, model_class, field_name):
        """获取表中某个字段的值列表，用于字段配置唯一约束时校验"""
        manager = cls._get_manager(model_class)
        return set(manager.all().values_list(field_name, flat=True))

    @classmethod
    def _generate_default_and_choices_value(cls, field):
        """根据字段默认值和选项生成对应值"""
        if field.default is not fields.NOT_PROVIDED:
            default_factor = cls._meta.field_to_faker_config.get(DEFAULT_VALUE_FACTOR, DEFAULT_DEFAULT_VALUE_FACTOR)
            if random.random() <= default_factor:
                return field.default, True

        if field.choices:
            return random.choice([choice[0] for choice in field.choices]), True

        return None, False
