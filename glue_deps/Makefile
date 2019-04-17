# Default S3 prefix
BUCKET_PREFIX?=glue-libs

s3_bucket: 
	@test -n "$(s3_bucket)" || (echo "'s3_bucket' variable must be defined" && exit 1)

release: s3_bucket
	python setup.py bdist_egg
	aws s3 sync --exclude '*' --include '*.egg' dist/ s3://$(s3_bucket)/$(BUCKET_PREFIX)/
