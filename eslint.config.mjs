// ESLint flat config for SparkIDE.
//
// Scope: the first-party Blockly sources only — block definitions and the
// Arduino generator. The vendored Blockly runtime (blockly/vendor/) is third
// party and intentionally excluded. The goal is catching real errors (syntax,
// undeclared vars, unused vars) rather than enforcing a style — ruff/prettier
// concerns don't belong here.
import js from '@eslint/js';
import globals from 'globals';

export default [
  {
    files: ['blockly/blocks/**/*.js', 'blockly/generators/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'script',
      globals: {
        ...globals.browser,
        Blockly: 'readonly',
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-unused-vars': ['warn', { args: 'none' }],
    },
  },
  {
    files: ['tests/**/*.{js,mjs}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: { ...globals.node },
    },
    rules: {
      ...js.configs.recommended.rules,
    },
  },
];
