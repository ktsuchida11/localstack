FROM localstack/lambda:python3.9
USER root
RUN pip install boto3 --user
ENTRYPOINT ["python"]
CMD ["/src/app.py"]