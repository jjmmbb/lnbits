from typing import Any, Optional

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect

from .db import core_app_extra, db
from .services import websocket_manager
from .views.admin_api import admin_router
from .views.api import api_router
from .views.auth_api import auth_router
from .views.extension_api import extension_router

# this compat is needed for usermanager extension
from .views.generic import generic_router
from .views.node_api import node_router, public_node_router, super_node_router
from .views.payment_api import payment_router
from .views.public_api import public_router
from .views.tinyurl_api import tinyurl_router
from .views.user_api import users_router
from .views.wallet_api import wallet_router
from .views.webpush_api import webpush_router
from .views.websocket_api import websocket_router

# backwards compatibility for extensions
core_app = APIRouter(tags=["Core"])


def init_core_routers() -> APIRouter:
    all_routers = APIRouter()
    all_routers.include_router(core_app)
    all_routers.include_router(generic_router)
    all_routers.include_router(auth_router)
    all_routers.include_router(admin_router)
    all_routers.include_router(node_router)
    all_routers.include_router(extension_router)
    all_routers.include_router(super_node_router)
    all_routers.include_router(public_node_router)
    all_routers.include_router(public_router)
    all_routers.include_router(payment_router)
    all_routers.include_router(wallet_router)
    all_routers.include_router(api_router)
    all_routers.include_router(websocket_router)
    all_routers.include_router(tinyurl_router)
    all_routers.include_router(webpush_router)
    all_routers.include_router(users_router)

    return all_routers


def enable_ws_tunnel_for_routers(routers: APIRouter):
    @routers.websocket("/api/v1/tunnel/{item_id}")
    async def websocket_connect(websocket: WebSocket, item_id: str):
        await websocket_manager.connect(websocket, item_id)
        try:
            while True:

                await websocket.receive_text()

                async def receive(message: Optional[Any] = None):
                    print("### receive", message)
                    return message

                async def send(message: Optional[Any] = None):
                    print("### send", message)
                    return message

                scope = {
                    "type": "http",
                    "method": "GET",
                    "path": "/api/v1/wallet",
                    "query_string": "",  # todo: test value
                    "headers": [(b"x-api-key", item_id.encode("utf-8"))],
                }
                #  b"65f14a3501624bb09279744b1865bffe"
                try:
                    await routers(scope, receive, send)
                    print("#### !!!")
                except WebSocketDisconnect:
                    websocket_manager.disconnect(websocket)
                except Exception as ex:
                    print("### ex2", ex)
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
