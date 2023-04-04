function writeArticle() {
    let title = $("#article-title").val();
    let category = $("input[name='category']:checked").val();

    if(category == "communication"){
        category = 1;
    }else if(category == "studyhard"){
        category = 2;
    }else if(category == "life"){
        category = 3;
    }
    
    let content = $("#article-content").val();

    // POST 방식으로 article 생성하기
    $.ajax({
        type: "POST",
        url: "/write",
        data: {title_give: title, category_give: category, content_give: content},
        success: function(response) {
            if(response["result"] == "success"){
                console.log("글 작성 성공!")
                alert("글 작성을 성공했습니다.");
                window.location.reload();
            }else {
                alert("글 작성을 실패했습니다.")
            }
        }
    })
}