window.onload = function () {
    var toc = '';

    document.getElementById("content_of_post").innerHTML =
        document.getElementById("content_of_post").innerHTML.replace(
            /<span id="(section[\d]+)">([^<]+)<\/span>/gi,
            function (str, sec_id, titleText) {
                toc += '<li class="nav-item"><a class="nav-link" href="#' + sec_id + "\">"
                    + titleText
                    + "</a></li>";

                return "<span id=\"" + sec_id + "\">" + titleText + "</span>";
            }
        );

    toc += "</ul>";
    document.getElementById("nav-sidebar").innerHTML += toc;
};
