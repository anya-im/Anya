FROM python:3.11-slim
WORKDIR /opt/anya/

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
COPY setup.py requirements.txt ./
RUN pip3 install -r requirements.txt

ADD anya .
RUN python3 setup.py install

ENTRYPOINT ["anya"]
