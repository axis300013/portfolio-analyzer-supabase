11:18:49
Machine started in 1.362s
11:18:49
machine started in 1.532456825s
11:18:49
2026/01/15 11:18:49 INFO SSH listening listen_address=[fdaa:3e:2450:a7b:502:4723:78ad:2]:22
11:18:50
    [ERROR] DATABASE_URL not found in environment variables!
11:18:50
    In Railway Dashboard, did you add the DATABASE_URL variable?
11:18:50
    Value should be:
11:18:50
    postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
11:18:50
    Check Railway Settings > Variables tab and verify DATABASE_URL is there.
11:18:50
Traceback (most recent call last):
11:18:50
  File "/usr/local/bin/uvicorn", line 7, in <module>
11:18:50
    sys.exit(main())
11:18:50
             ~~~~^^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 1485, in __call__
11:18:50
    return self.main(*args, **kwargs)
11:18:50
           ~~~~~~~~~^^^^^^^^^^^^^^^^^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 1406, in main
11:18:50
    rv = self.invoke(ctx)
11:18:50
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 1269, in invoke
11:18:50
    return ctx.invoke(self.callback, **ctx.params)
11:18:50
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 824, in invoke
11:18:50
    return callback(*args, **kwargs)
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/main.py", line 424, in main
11:18:50
    run(
11:18:50
    ~~~^
11:18:50
        app,
11:18:50
        ^^^^
11:18:50
    ...<46 lines>...
11:18:50
        h11_max_incomplete_event_size=h11_max_incomplete_event_size,
11:18:50
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11:18:50
    )
11:18:50
    ^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/main.py", line 594, in run
11:18:50
    server.run()
11:18:50
    ~~~~~~~~~~^^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/server.py", line 67, in run
11:18:50
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
11:18:50
  File "/usr/local/lib/python3.13/asyncio/runners.py", line 195, in run
11:18:50
    return runner.run(main)
11:18:50
           ~~~~~~~~~~^^^^^^
11:18:50
  File "/usr/local/lib/python3.13/asyncio/runners.py", line 118, in run
11:18:50
    return self._loop.run_until_complete(task)
11:18:50
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
11:18:50
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/server.py", line 71, in serve
11:18:50
    await self._serve(sockets)
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/server.py", line 78, in _serve
11:18:50
    config.load()
11:18:50
    ~~~~~~~~~~~^^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/config.py", line 439, in load
11:18:50
    self.loaded_app = import_from_string(self.app)
11:18:50
                      ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
11:18:50
  File "/usr/local/lib/python3.13/site-packages/uvicorn/importer.py", line 19, in import_from_string
11:18:50
    module = importlib.import_module(module_str)
11:18:50
  File "/usr/local/lib/python3.13/importlib/__init__.py", line 88, in import_module
11:18:50
    return _bootstrap._gcd_import(name[level:], package, level)
11:18:50
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11:18:50
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
11:18:50
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
11:18:50
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
11:18:50
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
11:18:50
  File "<frozen importlib._bootstrap_external>", line 1023, in exec_module
11:18:50
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
11:18:50
  File "/app/backend/app/main.py", line 7, in <module>
11:18:50
    from . import crud, models, wealth_crud
11:18:50
  File "/app/backend/app/crud.py", line 4, in <module>
11:18:50
    from . import models
11:18:50
  File "/app/backend/app/models.py", line 4, in <module>
11:18:50
    from .db import Base
11:18:50
  File "/app/backend/app/db.py", line 5, in <module>
11:18:50
    from .config import settings
11:18:50
  File "/app/backend/app/config.py", line 45, in <module>
11:18:50
    raise ValueError(error_msg)
11:18:50
ValueError:
11:18:50
    [ERROR] DATABASE_URL not found in environment variables!
11:18:50
    In Railway Dashboard, did you add the DATABASE_URL variable?
11:18:50
    Value should be:
11:18:50
    postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
11:18:50
    Check Railway Settings > Variables tab and verify DATABASE_URL is there.
11:18:51
 INFO Main child exited normally with code: 1
11:18:51
 INFO Starting clean up.
11:18:51
[    2.983542] reboot: Restarting system
11:18:51
machine has reached its max restart count of 10
11:18:54
waiting for machine to be reachable on 0.0.0.0:8000 (waited 5.175862749s so far)
11:18:59
[PM05] failed to connect to machine: gave up after 15 attempts (in 10.116362584s)
11:18:59
[PR04] could not find a good candidate within 40 attempts at load balancing
11:19:12
2026-01-15T11:19:12.315001397 [01KF0NKGMJW8866MYQ14GQHFTY:main] Running Firecracker v1.12.1
11:19:12
2026-01-15T11:19:12.315178457 [01KF0NKGMJW8866MYQ14GQHFTY:main] Listening on API socket ("/fc.sock").
11:19:13
 INFO Starting init (commit: 6f59af0a)...
11:19:13
 INFO Preparing to run: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` as root
11:19:13
 INFO [fly api proxy] listening at /.fly/api
11:19:13
2026/01/15 11:19:13 INFO SSH listening listen_address=[fdaa:3e:2450:a7b:502:4723:78ad:2]:22
11:19:13
Machine started in 1.362s
11:19:15
    [ERROR] DATABASE_URL not found in environment variables!
11:19:15
    In Railway Dashboard, did you add the DATABASE_URL variable?
11:19:15
    Value should be:
11:19:15
    postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
11:19:15
    Check Railway Settings > Variables tab and verify DATABASE_URL is there.
11:19:15
Traceback (most recent call last):
11:19:15
  File "/usr/local/bin/uvicorn", line 7, in <module>
11:19:15
    sys.exit(main())
11:19:15
             ~~~~^^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 1485, in __call__
11:19:15
    return self.main(*args, **kwargs)
11:19:15
           ~~~~~~~~~^^^^^^^^^^^^^^^^^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 1406, in main
11:19:15
    rv = self.invoke(ctx)
11:19:15
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 1269, in invoke
11:19:15
    return ctx.invoke(self.callback, **ctx.params)
11:19:15
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/click/core.py", line 824, in invoke
11:19:15
    return callback(*args, **kwargs)
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/main.py", line 424, in main
11:19:15
    run(
11:19:15
    ~~~^
11:19:15
        app,
11:19:15
        ^^^^
11:19:15
    ...<46 lines>...
11:19:15
        h11_max_incomplete_event_size=h11_max_incomplete_event_size,
11:19:15
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11:19:15
    )
11:19:15
    ^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/main.py", line 594, in run
11:19:15
    server.run()
11:19:15
    ~~~~~~~~~~^^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/server.py", line 67, in run
11:19:15
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
11:19:15
  File "/usr/local/lib/python3.13/asyncio/runners.py", line 195, in run
11:19:15
    return runner.run(main)
11:19:15
           ~~~~~~~~~~^^^^^^
11:19:15
  File "/usr/local/lib/python3.13/asyncio/runners.py", line 118, in run
11:19:15
    return self._loop.run_until_complete(task)
11:19:15
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
11:19:15
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/server.py", line 71, in serve
11:19:15
    await self._serve(sockets)
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/server.py", line 78, in _serve
11:19:15
    config.load()
11:19:15
    ~~~~~~~~~~~^^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/config.py", line 439, in load
11:19:15
    self.loaded_app = import_from_string(self.app)
11:19:15
                      ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
11:19:15
  File "/usr/local/lib/python3.13/site-packages/uvicorn/importer.py", line 19, in import_from_string
11:19:15
    module = importlib.import_module(module_str)
11:19:15
  File "/usr/local/lib/python3.13/importlib/__init__.py", line 88, in import_module
11:19:15
    return _bootstrap._gcd_import(name[level:], package, level)
11:19:15
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11:19:15
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
11:19:15
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
11:19:15
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
11:19:15
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
11:19:15
  File "<frozen importlib._bootstrap_external>", line 1023, in exec_module
11:19:15
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
11:19:15
  File "/app/backend/app/main.py", line 7, in <module>
11:19:15
    from . import crud, models, wealth_crud
11:19:15
  File "/app/backend/app/crud.py", line 4, in <module>
11:19:15
    from . import models
11:19:15
  File "/app/backend/app/models.py", line 4, in <module>
11:19:15
    from .db import Base
11:19:15
  File "/app/backend/app/db.py", line 5, in <module>
11:19:15
    from .config import settings
11:19:15
  File "/app/backend/app/config.py", line 45, in <module>
11:19:15
    raise ValueError(error_msg)
11:19:15
ValueError:
11:19:15
    [ERROR] DATABASE_URL not found in environment variables!
11:19:15
    In Railway Dashboard, did you add the DATABASE_URL variable?
11:19:15
    Value should be:
11:19:15
    postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
11:19:15
    Check Railway Settings > Variables tab and verify DATABASE_URL is there.
11:19:16
 INFO Main child exited normally with code: 1
11:19:16
 INFO Starting clean up.
11:19:16
[    4.022999] reboot: Restarting system
11:19:16
machine has reached its max restart count of 10