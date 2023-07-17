from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
from fastapi import FastAPI
from nicegui import ui
from typing import Callable
import asyncio
import functools
import httpx as r
#import psutil

try:
  apm = make_apm_client({
      'SERVICE_NAME': 'my_python_service',
      'SECRET_TOKEN': 'supersecrettoken',
      # SERVER_URL must be set to "fleet-server" if running as a docker container.
      # if running as a local python script, then set the url to "LOCALHOST"
      'SERVER_URL': 'http://fleet-server:8200',
      'ENVIRONMENT': 'development'
  })
except Exception as e:
  print('failed to create client')

app = FastAPI()

try:
  app.add_middleware(ElasticAPM, client=apm)
except Exception as e:
  print('failed to add APM Middleware')


@app.get("/custom_message/{message}")
async def custom_message(message: str):
    apm.capture_message(f"Custom Message: {message}")
    return {"message": f"Custom Message:  {message}"}


@app.get("/error")
async def throw_error():
    try:
        1 / 0
    except Exception as e:
        apm.capture_exception()
    return {"message": "Failed Successfully :)"}


def init(fastapi_app: FastAPI) -> None:
    @ui.page('/', title="APM Demo App")
    async def show():
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            ui.markdown('### APM DEMO')
            ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as right_drawer:
            ui.chat_message('Hello Elastic Stack User!',
                            name='APM Robot',
                            stamp='now',
                            avatar='https://robohash.org/apm_robot')
            ui.chat_message('This app is powered by NICEGUI and FastAPI with Elastic APM Instrumentation :)',
                            name='APM Robot',
                            stamp='now',
                            avatar='https://robohash.org/apm_robot')
            ui.chat_message('Please click a button to trigger an APM event.',
                            name='APM Robot',
                            stamp='now',
                            avatar='https://robohash.org/apm_robot')
        with ui.footer().style('background-color: #3874c8'):
            ui.label('APM DEMO PAGE')

        with ui.card():
            ui.label('Generate Error - Python')
            ui.button('Generate', on_click=python_error)

        with ui.card():
            ui.label('Generate Error - JS')
            ui.button('Generate', on_click=js_error)

        with ui.card():
            ui.label('Generate Custom Message')
            custom_message_text = ui.input(placeholder='Message')
            ui.button('Generate').on('click', handler=lambda: gen_custom_message(custom_message_text.value))

    ui.run_with(
        fastapi_app,
        storage_secret='supersecret',  # NOTE setting a secret is optional but allows for persistent storage per user
    )


async def io_bound(callback: Callable, *args: any, **kwargs: any):
    '''Makes a blocking function awaitable; pass function as first parameter and its arguments as the rest'''
    return await asyncio.get_event_loop().run_in_executor(None, functools.partial(callback, *args, **kwargs))


async def python_error():
    try:
        res = await io_bound(r.get, 'http://localhost:8000/error')
        ui.notify(res.text)
    except Exception as e:
        apm.capture_exception()
        ui.notify(f'{e}')


async def js_error():
    try:
        res = await ui.run_javascript('fetch("http://localhost:8000/error")')
        ui.notify(f'Message: Failed Successfully :)')
    except Exception as e:
        apm.capture_exception()
        ui.notify(f'{e}')


async def gen_custom_message(text_message):
    try:
        res = await io_bound(r.get, 'http://localhost:8000/custom_message/' + str(text_message))
        ui.notify(res.text)
    except Exception as e:
        apm.capture_exception()
        ui.notify(f'{e}')

init(app)

try:
  apm.capture_message('App Loaded, Hello World!')
except Exception as e:
  print('error: ' + e)

if __name__ == '__main__':
    print('Please start the app with the "uvicorn" command as shown in the start.sh script')
