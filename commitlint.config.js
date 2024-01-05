const Configuration = {
  /*
   * Resolve and load @commitlint/config-conventional from node_modules.
   * Referenced packages must be installed
   */
  extends: [
    '@commitlint/config-conventional'
  ],
  /*
   * Resolve and load conventional-changelog-atom from node_modules.
   * Referenced packages must be installed
   */
  formatter: '@commitlint/format',
  /*
   * Any rules defined here will override rules from @commitlint/config-conventional
   */
  rules: {
		'type-enum': [
			2,
			'always',
			[
				'feat',
				'fix',
				'docs',
				'style',
				'refactor',
				'test',
				'perf',
				'chore',
			],
    ],
      'content-rule': [2, 'always'],
  },
    plugins: [
        {
            rules: {
                'content-rule': ({subject}) => {
                    const pattern = /#\d+$|--story=\d+$|--bug=\d+$/;
                    return [
                        pattern.test(subject.trim()),
                        `Your subject should contain issue id`,
                    ];
                }
            }
        }
    ],
  /*
   * Functions that return true if commitlint should ignore the given message.
   */
  ignores: [
      (commit) => commit === '',
      (message) => message.includes('Merge'),
      (message) => message.includes('merge'),
      (message) => message.includes('ignore')
  ],
  /*
   * Whether commitlint uses the default ignore rules.
   */
  defaultIgnores: true,
  /*
   * Custom URL to show upon failure
   */
  helpUrl:
    'https://github.com/conventional-changelog/commitlint/#what-is-commitlint',
  /*
   * Custom prompt configs
   */
  prompt: {
    messages: {},
    questions: {
      type: {
        description: 'please input type:',
      },
    },
  },
};

module.exports = Configuration;
