FROM python:3.12-alpine

RUN addgroup -S lboxgroup && adduser -S -G lboxgroup lbox
RUN apk add build-base python3-dev libev-dev
RUN pip3 install pipx

USER lbox
ENV PATH=$PATH:/home/lbox/.local/bin
RUN pipx install lbox

CMD ["lbox"]

# start this container with:
# docker run
#     --name lbox                               # container name (put your own)
#     -v /host/path/to/litter:/var/www/litter   # temp files directory
#     -p 5000:8080                              # port mapping of choice
#     --user 1000:1000                          # user with rw access to the temp files directory
#     lboximage                                 # name given to this image (put your own)
