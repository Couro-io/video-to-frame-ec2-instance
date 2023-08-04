BASE_NAME=ffmpeg
DEPLOYMENT_BUCKET_NAME := ffmpeg
DEPLOYMENT_KEY := resources/aws-ffmpeg-converter/$(shell echo $(BASE_NAME)-$$RANDOM.zip)
STACK_NAME := $(BASE_NAME)-stack

FFMPEG_VERSION=6.0

clean:
	rm -rf ./build

build/bin/ffmpeg:
	mkdir -p build/bin
	rm -rf build/ffmpeg
	cd build; \
		curl -L https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/ffmpeg/7:6.0-5ubuntu2/ffmpeg_6.0.orig.tar.xz | tar x
	mv build/ffmpeg*/ffmpeg build/ffmpeg*/ffprobe build/bin

build/layer.zip: build/bin/ffmpeg
	cd build && zip -r layer.zip bin

build/output.yaml: build/layer.zip template.yaml

deploy: build/output.yaml
	aws s3 cp build/layer.zip s3://${DEPLOYMENT_BUCKET_NAME}/${DEPLOYMENT_KEY}
	sed "s:DEPLOYMENT_BUCKET_NAME:$(DEPLOYMENT_BUCKET_NAME):;:DEPLOYMENT_KEY:$(DEPLOYMENT_KEY)" template.yaml > build/output.yaml
	aws cloudformation deploy --template-file build/output.yaml --stack-name $(STACK_NAME)
	aws cloudformation describe-stacks --stack-name $(STACK_NAME) --query Stacks[].Outputs[].OutputValue --output text