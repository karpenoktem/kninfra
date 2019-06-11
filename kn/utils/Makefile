# Makefile to automate updating gRPC protobuf files.

all: hans/hans_pb2_grpc.py
.PHONY: all
hans/hans_pb2_grpc.py hans/hans_pb2.py: hans/hans.proto
	python -m grpc_tools.protoc -I./hans --python_out=hans --grpc_python_out=hans hans/hans.proto
