window.onload = function () {
    var toc = '<ul class="nav nav-pills flex-column">';
    var level = 2;
    var sec_id = 1;
    var nav_scroll_level = 2;

    document.getElementById("content_of_post").innerHTML =
        document.getElementById("content_of_post").innerHTML.replace(
            /<h([\d])>([^<]+)<\/h([\d])>/gi,
            function (str, openLevel, titleText, closeLevel) {
                if (openLevel != closeLevel) {
                    return str;
                }

                if (openLevel > level) {
                    toc += (new Array(openLevel - level + 1)).join('<ul>');
                } else if (openLevel < level) {
                    toc += (new Array(level - openLevel + 1)).join("</ul>");
                }

                level = parseInt(openLevel);

                if (openLevel <= nav_scroll_level){
                    var anchor = "section" + sec_id;
                    sec_id++;
                    toc += '<li class="nav-item"><a class="nav-link" href="#' + anchor + "\">"
                        + titleText
                        + "</a></li>";
                } else {
                    toc += '<li>' + titleText + "</li>";
                }

                return "<h" + openLevel + ">" + titleText + "</h" + closeLevel + ">";
            }
        );

    if (level) {
        toc += (new Array(level + 1)).join("</ul>");
    }

    document.getElementById("nav-sidebar").innerHTML += toc;
};
