import os

from flask import Flask, render_template
import grpc

from recommendations_pb2 import BookCategory, RecommendationRequest
from recommendations_pb2_grpc import RecommendationsStub

app = Flask(__name__)

# В этом примере мы создаем канал и заглушку gRPC как глобальные объекты. Обычно глобальные переменные запрещены,
# но в этом случае требуется исключение.Канал gRPC поддерживает постоянное соединение с сервером, чтобы избежать
# накладных расходов, связанных с повторным подключением. Он может обрабатывать множество одновременных запросов и
# восстанавливать разорванные соединения. Однако, если мы создаем новый канал перед каждым запросом, Python будет
# собирать их с помощью сборщика мусора, и мы потеряем большинством преимуществ.Мы хотим, чтобы канал оставался
# открытым и нам не приходилось повторно подключаться к микросервису рекомендаций для каждого запроса. Мы можем
# скрыть канал внутри другого модуля, но поскольку в этом случае у нас есть только один файл, мы можем упростить
# задачу, используя глобальные переменные.

recommendations_host = os.getenv("RECOMMENDATIONS_HOST", "localhost")
recommendations_channel = grpc.insecure_channel(
    f"{recommendations_host}:50051"
)
recommendations_client = RecommendationsStub(recommendations_channel)


@app.route("/")
def render_homepage():
    recommendations_request = RecommendationRequest(
        user_id=1, category=BookCategory.MYSTERY, max_results=3
    )
    recommendations_response = recommendations_client.Recommend(
        recommendations_request
    )
    return render_template(
        "homepage.html",
        recommendations=recommendations_response.recommendations,
    )
