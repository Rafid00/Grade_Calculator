let open = false;

for (let i = 0; i <= 3; i++) {
   let width = $($(".left ul li")[i]).outerWidth();
   $($(".left ul li")[i]).mouseover(function () {
      $($(".left ul li")[i]).append('<div class="line"></div>');
      $(".line").css("width", width);
      $(".line").css("animation", "fadeIn-2 0.3s both");
   });
}

for (let i = 0; i <= 3; i++) {
   $($(".left ul li")[i]).mouseout(function () {
      $(".line").remove();
   });
}

$(".right img").click(function () {
   if (open === false) {
      $(".right-ul-default").css("animation", "fadeIn 0.2s both");
      $(".right-ul-default").css("display", "flex");
      open = true;
      $("section").click(function () {
         if (open === true) {
            setTimeout(`$(".right-ul-default").css("display", "none")`, 200);
            $(".right-ul-default").css("animation", "fadeOut 0.2s both");
            open = false;
         }
      });
   } else {
      setTimeout(`$(".right-ul-default").css("display", "none")`, 200);
      $(".right-ul-default").css("animation", "fadeOut 0.2s both");
      open = false;
   }
});