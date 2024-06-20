from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from urllib.parse import unquote
import shutil
import tempfile
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from datetime import datetime, timedelta
import base64

utils_router = APIRouter()
scheduler = BackgroundScheduler()
scheduler.start()


def delete_file(path):
    Path(path).unlink(missing_ok=True)


@utils_router.get("/readfile/")
async def process_file(temp_path: str):
    try:
        # 解码 URL 获得实际文件路径
        decoded_url = unquote(temp_path)
        file_name = temp_path.split("/")[-1]
        # 假设实际文件存储在服务器的 'temporary' 目录下，并从 URL 中提取文件名
        file_path = Path(tempfile.gettempdir()) / file_name
        # 检查文件是否存在
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # 读取文件内容
        with file_path.open("rb") as file:
            file_data = file.read()

        # 获取文件大小
        file_size = file_path.stat().st_size

        # 提取文件扩展名
        file_extension = file_name.split(".")[-1]

        file_data_base64 = base64.b64encode(file_data).decode("utf-8")

        return {
            "filename": file_name,
            "extension": file_extension,
            "file_size": file_size,
            "file_data": file_data_base64,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@utils_router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    temp_file = None  # 初始化变量以确保其作用域覆盖整个函
    try:
        # 创建临时文件，并保留路径供后续使用
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        )
        shutil.copyfileobj(file.file, temp_file.file)
        temp_file_path = Path(temp_file.name)  # 保存路径
    except Exception as e:
        # 如果在文件操作中出现异常，提供错误信息
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 确保临时文件被关闭
        if temp_file:
            temp_file.close()

    try:
        # 使用请求信息构建文件URL
        server_host = request.url.hostname
        server_port = request.url.port
        run_date = datetime.now() + timedelta(hours=1)
        scheduler.add_job(delete_file, "date", run_date=run_date, args=[temp_file_path])
        file_url = f"http://{server_host}:{server_port}/temp/{temp_file_path.name}"
        return {"filename": file.filename, "url": file_url}
    except Exception as e:
        # 如果URL构建或其他操作失败
        raise HTTPException(
            status_code=500, detail=f"Failed to create file URL: {str(e)}"
        )
