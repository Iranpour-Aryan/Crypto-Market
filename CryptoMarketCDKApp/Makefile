release: node_modules .pipenv

lint:
	pipenv run black --line-length 120 serverless_flask
	pipenv run flake8 serverless_flask

clean:
	del /s /q .\**\*.pyc
	for /d /r .\ /f %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"
	rmdir /s /q cdk.out
	rmdir /s /q build-python
	rmdir /s /q .aws-sam
	del /f requirements.txt
	del /f .deploy-dev-once
	rmdir /s /q node_modules
	del /f sam-params.json
	del /f test\*.js
	del /f .pipenv && pipenv --rm || true
	echo Clean is finished

.pipenv:
	pipenv lock
	pipenv sync -d

run-flask: .pipenv .deploy-dev-once
	set "FLASK_APP=serverless_flask:create_app"
	set "JSON_CONFIG_OVERRIDE=`jq -r '."serverless-flask-dev".LambdaEnv' cdk.out\dev-stage-output.json`"
	set "AWS_PROFILE=serverless-flask-dev"
	set "FLASK_ENV=dev"
	set "FLASK_DEBUG=1"
	pipenv run flask run --cert adhoc -h localhost -p 5000

update-deps: clean
	pipenv update

build-python: .pipenv
	echo "Building in $@/"
	pipenv requirements > requirements.txt
	pip install -r requirements.txt -t "$@/"
	rmdir /s /q "$@/boto3"
	rmdir /s /q "$@/botocore"
	for /d /r "%CD%\build-python" %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"
	del /s /q "%CD%\build-python\*.pyc"

bundle-python:
	echo Copying local Python files
	robocopy /s /ndl /njh /njs serverless_flask "%CD%\build-python\serverless_flask"
	echo "The Python bundle's size: $$(du -sh "build-python/")"

pytest:
	pipenv run pytest -x

npmtest: build-ts bundle-python
	npm run test

test: pytest npmtest

build-ts:
	npm run build

node_modules:
	npm install

deploy-dev: node_modules bundle-python
	cdk deploy -c stage=dev --outputs-file cdk.out\dev-stage-output.json

.deploy-dev-once: node_modules
	cdk deploy -c stage=dev --outputs-file cdk.out\dev-stage-output.json
	touch $@

deploy-staging:
	cdk deploy -c stage=staging

deploy-prod:
	cdk deploy -c stage=prod

synth-dev: node_modules
	cdk synth -c stage=dev

sam-params.json:
	jq -r '{"Parameters":{"JSON_CONFIG_OVERRIDE": ."serverless-flask-dev".LambdaEnv}}' cdk.out\dev-stage-output.json > "$@"

sam-local: .deploy-dev-once bundle-python synth-dev sam-params.json
	sam local start-api -p 5000 -t cdk.out\ServerlessFlask.template.json -n sam-params.json
	del /f sam-params.json

.PHONY: clean run-flask bundle-python build-ts test pytest npmtest sam-local deploy-dev deploy-staging deploy-prod release update-deps synth-dev npm-install lint

