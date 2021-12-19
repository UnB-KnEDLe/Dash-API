FROM python:3.8

ENV PATH /root/.local/bin:$PATH
COPY ./ /api
RUN pip install -r ./api/requirements.txt
WORKDIR api
EXPOSE 9001
CMD ["python", "api.py"]