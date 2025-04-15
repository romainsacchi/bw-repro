rule run:
	input:
		'workflow/config/config.json'

	output:
		'workflow/results/results.txt'
	conda:
		'envs/env.yaml'
	threads: 1
	script:
		'scripts/script.py'