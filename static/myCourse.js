let current_event_target;
let button_name;

// ADD BUTTON

$(".add-course-btn").click(function () {
   $(".submit-btn button").text("Add Course");
   button_name = "Add Course";
   // adding animation
   $(".add-course-pop").css("animation", "pop-up 0.6s both");
   $(".dark-bg").css("animation", "fade 0.6s both");
   //  empty input fields
   $(".input-col input").val("");
   //  display to block
   $(".add-course-pop, .dark-bg").css("display", "block");
   $(".close-btn img").click(function () {
      setTimeout(`$(".add-course-pop").css("display", "none")`, 400);
      $(".add-course-pop").css("animation", "pop-down 0.5s both");
      setTimeout(`$(".dark-bg").css("display", "none")`, 200);
      $(".dark-bg").css("animation", "fade-away 0.2s both");
   });
   $(".dark-bg").click(function () {
      $(".add-course-pop").css("animation", "pop-down 0.5s both");
      setTimeout(`$(".add-course-pop").css("display", "none")`, 400);
      $(".dark-bg").css("animation", "fade-away 0.2s both");
      setTimeout(`$(".dark-bg").css("display", "none")`, 200);
   });
});

$(".add-course-pop-form").on("submit", function (event) {
   if (button_name == "Add Course") {
      let course_init = $("#course-init").val();
      let grade = $("#grade").val();
      let total_marks = $("#total-marks").val();
      let credit = $("#credit").val();
      let action = "add-course";
      $.ajax({
         data: {
            course_init: course_init,
            grade: grade,
            total_marks: total_marks,
            credit: credit,
            action: action,
         },
         type: "POST",
         url: "/mycourses",
      }).done(function (data) {
         if (data.error) {
         } else {
            $(".course-list").append(`<div class="course-item">
   <div class="move-retake-btn">
      <img src="../static/images/move.svg" alt="" title="Move to 'Retake Output'" />
   </div>
   <div class="course-info">
      <div class="course-init">Course Init : <span class="text-value">${course_init}</span></div>
      <div class="grade">Grade : <span class="text-value">${data.grade_marks}</span></div>
      <div class="grade-point">Grade Point : <span class="text-value">${parseFloat(data.grade_point).toFixed(3)}</span></div>
      <div class="credit">Credit : <span class="text-value">${credit}</span></div>
   </div>
   <div class="edit-delete-btn">
      <div class="edit-btn"><img src="../static/images/edit.svg" alt="" title="Edit" /></div>
      <div class="delete-btn"><img src="../static/images/delete.svg" alt="" title="Delete" /></div>
   </div>
</div>`);
            $(".gpa-val").text(data.cgpa)
            $(".creditPassed-val").text(data.creditPassed)
         }
         setTimeout(`$(".add-course-pop").css("display", "none")`, 400);
         $(".add-course-pop").css("animation", "pop-down 0.5s both");
         setTimeout(`$(".dark-bg").css("display", "none")`, 200);
         $(".dark-bg").css("animation", "fade-away 0.2s both");
      });
   } else if (button_name == "Edit Course") {
      let course_init = $("#course-init").val();
      let grade = $("#grade").val();
      let total_marks = $("#total-marks").val();
      let credit = $("#credit").val();
      let action = "edit-course";

      let prev_course_init = $(current_event_target).closest(".course-item").find(".course-init .text-value").text();
      let prev_grade = $(current_event_target).closest(".course-item").find(".grade .text-value").text();
      let prev_grade_point = $(current_event_target).closest(".course-item").find(".grade-point .text-value").text();
      let prev_credit = $(current_event_target).closest(".course-item").find(".credit .text-value").text();

      $.ajax({
         data: {
            course_init: course_init,
            grade: grade,
            total_marks: total_marks,
            credit: credit,
            action: action,
            prev_course_init: prev_course_init,
            prev_grade: prev_grade,
            prev_grade_point: prev_grade_point,
            prev_credit: prev_credit,
         },
         type: "POST",
         url: "/mycourses",
      }).done(function (data) {
         $(current_event_target).closest(".course-item").find(".course-init .text-value").text(course_init);
         $(current_event_target).closest(".course-item").find(".grade .text-value").text(data.grade_marks);
         $(current_event_target).closest(".course-item").find(".grade-point .text-value").text(data.grade_point);
         $(current_event_target).closest(".course-item").find(".credit .text-value").text(credit);
         $(".gpa-val").text(data.cgpa)
         $(".creditPassed-val").text(data.creditPassed)

         setTimeout(`$(".add-course-pop").css("display", "none")`, 400);
         $(".add-course-pop").css("animation", "pop-down 0.5s both");
         setTimeout(`$(".dark-bg").css("display", "none")`, 200);
         $(".dark-bg").css("animation", "fade-away 0.2s both");
      });
   }

   event.preventDefault();
});

$(".course-list").on("click", function (event) {
   if ($(event.target).is(".delete-btn img")) {
      let course_init = $(event.target).closest(".course-item").find(".course-init .text-value").text();
      let grade = $(event.target).closest(".course-item").find(".grade .text-value").text();
      let grade_point = $(event.target).closest(".course-item").find(".grade-point .text-value").text();
      let credit = $(event.target).closest(".course-item").find(".credit .text-value").text();
      let action = "delete";

      $.ajax({
         data: {
            course_init: course_init,
            grade: grade,
            grade_point: grade_point,
            credit: credit,
            action: action,
         },
         type: "POST",
         url: "/mycourses",
      }).done(function (data) {
         setTimeout(function () {
            $(event.target).closest(".course-item").remove();
         }, 420);
         $(event.target).closest(".course-item").fadeOut(400);
         $(".gpa-val").text(data.cgpa)
         $(".creditPassed-val").text(data.creditPassed)
      });
   } else if ($(event.target).is(".edit-btn img")) {
      button_name = "Edit Course";
      // adding animation
      $(".add-course-pop").css("animation", "pop-up 0.6s both");
      $(".dark-bg").css("animation", "fade 0.6s both");
      //  adding input fields
      $("#course-init").val($(event.target).closest(".course-item").find(".course-init .text-value").text());
      $("#grade").val($(event.target).closest(".course-item").find(".grade .text-value").text());
      $("#credit").val($(event.target).closest(".course-item").find(".credit .text-value").text());
      $("#total-marks").val("");
      // button name change
      $(".submit-btn button").text("Commit Changes");
      //  display to block
      $(".add-course-pop, .dark-bg").css("display", "block");
      $(".close-btn img").click(function () {
         setTimeout(`$(".add-course-pop").css("display", "none")`, 400);
         $(".add-course-pop").css("animation", "pop-down 0.5s both");
         setTimeout(`$(".dark-bg").css("display", "none")`, 200);
         $(".dark-bg").css("animation", "fade-away 0.2s both");
         setTimeout(`$(".submit-btn button").text("Add Course");`, 600);
      });
      $(".dark-bg").click(function () {
         $(".add-course-pop").css("animation", "pop-down 0.5s both");
         setTimeout(`$(".add-course-pop").css("display", "none")`, 400);
         $(".dark-bg").css("animation", "fade-away 0.2s both");
         setTimeout(`$(".dark-bg").css("display", "none")`, 200);
         setTimeout(`$(".submit-btn button").text("Add Course");`, 600);
      });

      current_event_target = event.target;
   } else if ($(event.target).is(".move-retake-btn img")) {
      let course_init = $(event.target).closest(".course-item").find(".course-init .text-value").text();
      let grade = $(event.target).closest(".course-item").find(".grade .text-value").text();
      let grade_point = $(event.target).closest(".course-item").find(".grade-point .text-value").text();
      let credit = $(event.target).closest(".course-item").find(".credit .text-value").text();
      let action = "move-retake-course";

      $.ajax({
         data: {
            course_init: course_init,
            grade: grade,
            grade_point: grade_point,
            credit: credit,
            action: action,
         },
         type: "POST",
         url: "/mycourses",
      }).done(function (data) {
         setTimeout(function () {
            $(event.target).closest(".course-item").remove();
         }, 420);
         $(event.target).closest(".course-item").fadeOut(400);
         $(".gpa-val").text(data.cgpa)
         $(".creditPassed-val").text(data.creditPassed)
      });
   }
});
