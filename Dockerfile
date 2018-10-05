FROM python:3.7.0-alpine3.7
# RUN apk add --no-cache mariadb-dev build-base
ENV PYTHONUNBUFFERED 1
RUN mkdir /benefit-rules-calculator-back-end/
WORKDIR /benefit-rules-calculator-back-end/
ADD . /benefit-rules-calculator-back-end/

RUN mv /benefit-rules-calculator-back-end/mysql/config/.mylogin.cnf /root
RUN chmod 740 /root/.mylogin.cnf

# https://github.com/gliderlabs/docker-alpine/issues/181#issuecomment-348608168
RUN apk add --no-cache --virtual build-dependencies build-base mariadb-dev \
	&& pip install -qq -r requirements.txt \
	&& rm -rf .cache/pip \
	&& apk del build-dependencies
RUN apk --no-cache add mariadb-client-libs
RUN apk --no-cache add mariadb-client
WORKDIR /benefit-rules-calculator-back-end/src/

ENV DJANGO_SETTINGS_MODULE=BenefitCalculator.production-settings

RUN chmod +x /benefit-rules-calculator-back-end/wait-for-mysql.sh
ENTRYPOINT ["/benefit-rules-calculator-back-end/wait-for-mysql.sh"]
CMD ["gunicorn", "BenefitCalculator.wsgi", "-b", "0.0.0.0:8001", "--workers", "4", "--timeout", "60"]