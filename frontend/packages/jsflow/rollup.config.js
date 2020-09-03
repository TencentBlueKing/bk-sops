import resolve from 'rollup-plugin-node-resolve'
import commonjs from 'rollup-plugin-commonjs'
import vue from 'rollup-plugin-vue'
import json from 'rollup-plugin-json'
import babel from 'rollup-plugin-babel'
import { uglify } from 'rollup-plugin-uglify'
import { terser } from 'rollup-plugin-terser'

const builds = [
    {
        name: 'jsflow-umd',
        dest: 'dist/jsflow.js',
        format: 'umd',
        env: 'production'
    },
    {
        name: 'jsflow-umd-min',
        dest: 'dist/jsflow.min.js',
        format: 'umd',
        env: 'production'
    },
    {
        name: 'jsflow-es-module',
        dest: 'dist/jsflow.esm.js',
        format: 'es',
        env: 'production'
    }
]

const plugins = [
    commonjs(),
    vue({
        template: {
            isProduction: true,
            compilerOptions: {
                preserveWhitespace: false
            }
        }
    }),
    json(),
    resolve({
        jsnext: true,
        main: true,
        browser: true,
        extensions: ['.js', '.vue'],
        modulesOnly: true
    }),
    babel({
        babelrc: false,
        exclude: 'node_modules/**',
        runtimeHelpers: true,
        presets: [
            [ '@babel/env', { 'modules': false } ]
        ],
        extensions: ['js', 'vue', 'ts'],
        comments: true
    })
]

const configs = builds.map(build => {
    const isProd = build.env === 'production'
    const minify = build.format === 'es' ? terser : uglify

    return {
        input: 'src/index.js',
        output: {
            file: build.dest,
            format: build.format,
            name: build.name,
            globals: {
                vue: 'Vue',
                jsplumb: 'jsplumb'
            }
        },
        external: ['vue', 'jsplumb'],
        plugins: isProd ? plugins.concat(minify()) : plugins
    }
})

export default configs
