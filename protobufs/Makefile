# Makefile to automate updating gRPC protobuf files.

.PHONY: all clean
all: messages/common_pb2_grpc.py messages/daan_pb2_grpc.py messages/hans_pb2_grpc.py

clean:
	find messages/ -name '*_pb2*' -delete

messages/common_pb2_grpc.py messages/common_pb2.py: messages/common.proto
	python -m grpc_tools.protoc -I.. --python_out=.. --grpc_python_out=.. protobufs/messages/common.proto

messages/daan_pb2_grpc.py messages/daan_pb2.py: messages/daan.proto
	python -m grpc_tools.protoc -I.. --python_out=.. --grpc_python_out=.. protobufs/messages/daan.proto

messages/hans_pb2_grpc.py messages/hans_pb2.py: messages/hans.proto
	python -m grpc_tools.protoc -I.. --python_out=.. --grpc_python_out=.. protobufs/messages/hans.proto
