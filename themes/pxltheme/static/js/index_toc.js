window.onload = function () {
    var toc = '<ul class="fa-ul">';

    document.getElementById("content_of_post").innerHTML =
        document.getElementById("content_of_post").innerHTML.replace(
            /<span id="(section[\d]+)">([^<]+)<\/span>/gi,
            function (str, sec_id, titleText) {
                toc += '<li class="nav-item"><a class="nav-link" href="#' + sec_id + "\">"
                    + '<i class="fa-li fa fa-arrow-circle-right"></i> '
                    + titleText
                    + "</a></li>";

                return "<span id=\"" + sec_id + "\">" + titleText + "</span>";
            }
        );

    toc += "</ul>";
    document.getElementById("nav-sidebar").innerHTML += toc;
};
