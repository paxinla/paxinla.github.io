window.onload = function () {
    var toc = '<ul class="fa-ul">';
    var postsShowOnIndexPage = document.getElementById("content_of_post").children;
    var latest3Posts = '';

    for (let i=0; i<3; i++){
        latest3Posts += postsShowOnIndexPage[i].innerHTML ;
    }

    latest3Posts.replace(
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
