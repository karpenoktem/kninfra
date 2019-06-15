# Makefile to automate updating gRPC protobuf files.

.PHONY: all
all: hans/hans_pb2_grpc.py daan/daan_pb2_grpc.py

daan/daan_pb2_grpc.py daan/daan_pb2.py: daan/daan.proto
	python -m grpc_tools.protoc -I./daan --python_out=daan --grpc_python_out=daan daan/daan.proto

hans/hans_pb2_grpc.py hans/hans_pb2.py: hans/hans.proto
	python -m grpc_tools.protoc -I./hans --python_out=hans --grpc_python_out=hans hans/hans.proto
