
(function(document, window, undefined) {

    function request(method, url, payload, headers) {
        return new Promise(function(resolve, reject) {
            var req = new XMLHttpRequest();
            req.open(method, url, true);
            if (headers) {
                for (var i = 0; i < headers.length; i++) {
                    req.setRequestHeader(headers[i][0], headers[i][1]);
                }
            }
            req.onload = function() {
                var resp;
                try {
                    resp = JSON.parse(req.response);
                } catch (err) {
                    resp = {
                        "status": req.status,
                        "reason": req.statusText,
                        "message": req.response
                    };
                }
                if (req.status == 200) {
                    resolve(resp);
                } else {
                    reject(resp);
                }
            };
            req.send(payload);
        });
    }

    function human_timeleft(time) {
        const secs_day = 24 * 60 * 60;
        var days = 0;
        var str = "";
        if (time < 0) {
            time = -time;
            str += "overdue ";
        }
        if (time > secs_day) {
            days = Math.floor(time / secs_day);
            time -= days*secs_day;
        }
        if (days > 0) {
            str += days + " days ";
        }
        var hours = new Date(time * 1000).toISOString().slice(11, 19);
        str += hours;
        return str;
    }

    function create_file_element(filename, size, timeleft) {
        const strtimeleft = human_timeleft(timeleft);
        var filediv = document.createElement("tr");
        var filepart = document.createElement("td");
        filepart.classList.add("filepart");
        filepart.innerHTML = '<a href="/file/' + filename + '">' + filename + '</a>';
        var sizepart = document.createElement("td");
        sizepart.innerText = size;
        var ttlpart = document.createElement("td");
        //ttlpart.classList.add("ttlpart");
        ttlpart.innerText = strtimeleft;
        if (timeleft < 300)
            ttlpart.classList.add("expiring");
        filediv.appendChild(filepart);
        filediv.appendChild(sizepart);
        filediv.appendChild(ttlpart);
        return filediv;
    }

    function show_error(err) {
        var container = document.getElementsByClassName("container")[0];
        container.innerText(err);
    }

    window.onload = async function() {
        var filelistarea = document.getElementsByClassName("filelist")[0];

        try {
            var filelist = await request("GET", "/file/");
        } catch (err) {
            show_error(err);
            return;
        }

        for (const f of filelist.files) {
            var filename = f[0];
            var size = f[1];
            var timeleft = f[2];
            var element = create_file_element(filename, size, timeleft);
            filelistarea.append(element);
        }

    };

})(document, window);
