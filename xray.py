#!/usr/bin/env python3

from grpc import insecure_channel, RpcError
from app.proxyman.command.command_pb2 import AddUserOperation, RemoveUserOperation, AlterInboundRequest
from app.proxyman.command.command_pb2_grpc import HandlerServiceStub
from app.stats.command.command_pb2 import QueryStatsRequest
from app.stats.command.command_pb2_grpc import StatsServiceStub
from common.protocol.user_pb2 import User
from common.serial.typed_message_pb2 import TypedMessage
from proxy.vless.account_pb2 import Account


class XrayController:
    def __init__(self, api_address, api_port):
        self.cmd_conn = insecure_channel(f"{api_address}:{api_port}")
        self.hs_client = HandlerServiceStub(self.cmd_conn)
        self.ss_client = StatsServiceStub(self.cmd_conn)


def add_vless_user(client, uuid, level, in_tag, email):
    operation = AddUserOperation(
        user=User(
            level=level,
            email=email,
            account=TypedMessage(
                type="xray.proxy.vless.Account",
                value=Account(id=uuid).SerializeToString()
            )
        )
    )

    request = AlterInboundRequest(
        tag=in_tag,
        operation=TypedMessage(
            type="xray.app.proxyman.command.AddUserOperation",
            value=operation.SerializeToString()
        )
    )

    return client.AlterInbound(request)


def remove_vless_user(client, in_tag, email):
    operation = RemoveUserOperation(email=email)

    request = AlterInboundRequest(
        tag=in_tag,
        operation=TypedMessage(
            type="xray.app.proxyman.command.RemoveUserOperation",
            value=operation.SerializeToString()
        )
    )

    return client.AlterInbound(request)


def query_traffic(client, pattern=None, reset=False):
    request = QueryStatsRequest(pattern=pattern, reset=reset)

    return client.QueryStats(request)
