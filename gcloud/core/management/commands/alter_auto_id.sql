-- Celery Beat 相关模型
ALTER TABLE django_celery_beat_clockedschedule AUTO_INCREMENT = 10000;
ALTER TABLE django_celery_beat_crontabschedule AUTO_INCREMENT = 10000;
ALTER TABLE django_celery_beat_periodictask AUTO_INCREMENT = 10000;

-- Pipeline 相关模型
ALTER TABLE pipeline_pipelinetemplate AUTO_INCREMENT = 100000;
ALTER TABLE pipeline_pipelineinstance AUTO_INCREMENT = 50000000;
ALTER TABLE pipeline_snapshot AUTO_INCREMENT = 50000000;
ALTER TABLE pipeline_templateversion AUTO_INCREMENT = 200000;
ALTER TABLE pipeline_templatecurrentversion AUTO_INCREMENT = 100000;
ALTER TABLE pipeline_templaterelationship AUTO_INCREMENT = 500000;
ALTER TABLE pipeline_templatescheme AUTO_INCREMENT = 100000;
ALTER TABLE pipeline_treeinfo AUTO_INCREMENT = 50000000;

-- Taskflow 相关模型
ALTER TABLE taskflow3_taskflowinstance AUTO_INCREMENT = 50000000;
ALTER TABLE tasktmpl3_tasktemplate AUTO_INCREMENT = 500000;

-- ERI 执行引擎模型
ALTER TABLE eri_callbackdata AUTO_INCREMENT = 50000000;
ALTER TABLE eri_contextoutputs AUTO_INCREMENT = 50000000;
ALTER TABLE eri_contextvalue AUTO_INCREMENT = 200000000;
ALTER TABLE eri_data AUTO_INCREMENT = 200000000;
ALTER TABLE eri_executiondata AUTO_INCREMENT = 100000000;
ALTER TABLE eri_executionhistory AUTO_INCREMENT = 1000000;
ALTER TABLE eri_node AUTO_INCREMENT = 300000000;
ALTER TABLE eri_process AUTO_INCREMENT = 100000000;
ALTER TABLE eri_schedule AUTO_INCREMENT = 100000000;
ALTER TABLE eri_state AUTO_INCREMENT = 200000000;

-- 其他业务模型
ALTER TABLE periodictask_periodictask AUTO_INCREMENT = 10000;
ALTER TABLE periodic_task_periodictask AUTO_INCREMENT = 10000;
ALTER TABLE files_fileuploadrecord AUTO_INCREMENT = 10000;
ALTER TABLE files_uploadticket AUTO_INCREMENT = 10000;
ALTER TABLE operate_record_taskoperaterecord AUTO_INCREMENT = 10000000;
ALTER TABLE operate_record_templateoperaterecord AUTO_INCREMENT = 1000000;
ALTER TABLE pipeline_web_core_nodeininstance AUTO_INCREMENT = 50000000;
ALTER TABLE pipeline_web_core_nodeintemplate AUTO_INCREMENT = 10000000;
ALTER TABLE periodictask_periodictaskhistory AUTO_INCREMENT = 50000000;
ALTER TABLE periodic_task_periodictaskhistory AUTO_INCREMENT = 50000000;
ALTER TABLE core_staffgroupset AUTO_INCREMENT = 1000;
ALTER TABLE project_constants_projectconstant AUTO_INCREMENT = 1000;
ALTER TABLE label_label AUTO_INCREMENT = 2000;
ALTER TABLE label_templatelabelrelation AUTO_INCREMENT = 20000;
ALTER TABLE appmaker_appmaker AUTO_INCREMENT = 2000;
ALTER TABLE clocked_task_clockedtask AUTO_INCREMENT = 2000;
ALTER TABLE collection_collection AUTO_INCREMENT = 10000;
ALTER TABLE function_functiontask AUTO_INCREMENT = 10000;
