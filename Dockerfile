FROM python:3.9.2
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot
CMD python "./Hu Tao Bot/main.py"