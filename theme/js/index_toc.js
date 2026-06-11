window.onload = function () {
    // 左侧导航栏的最近文章列表
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

    // 去除首页的注解元素
    var divClassToRemove = ['.sidenote', '.marginnote'];
    for (let c in divClassToRemove){
        let divClassName = divClassToRemove[c];
        let allDivsToRemove = document.querySelectorAll(divClassName);
        allDivsToRemove.forEach(function(e){e.parentNode.removeChild(e)});
    }
};
