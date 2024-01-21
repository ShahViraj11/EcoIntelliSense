


//Global variables
var carousel_count = 0,
    carousel_images = ['/images/slideshow/slide1.jpg', '/images/slideshow/slide2.jpg', '/images/slideshow/slide3.jpg'],
    looper = setInterval(function () {
        right_arrow();
    }, 3000);


$("header").hover(
    function () {
        clearInterval(looper);
    },
    function () {
        looper = setInterval(function () {
            right_arrow();
        }, 3000);
    }
);

function right_arrow() {
    carousel_count++;
    $(".carousel_arrows").children().css("opacity", "0.7");
    $(".right_arrow").css("opacity", "1");
    carousel();
}

function left_arrow() {
    carousel_count--;
    $(".carousel_arrows").children().css("opacity", "0.7");
    $(".left_arrow").css("opacity", "1");
    carousel();
}

function carousel() {
    $(".carousel_count li").removeClass("active");
    if (carousel_count < 0) {
        carousel_count = carousel_images.length - 1;
    }
    if (carousel_count > 2) {
        carousel_count = 0;
    }
    $(".carousel_count li:nth-child(" + parseInt(carousel_count + 1) + ")").addClass("active");
    $('.carousel').html('<img src="' + carousel_images[carousel_count] + '" alt="" class="blizer" />   <div class="centered">EcoIntelli Sense</div> <div class="para">AI-Driven Environmental Impact Analyzer</div>');
}


//WindowOnScroll
window.onscroll = function () {
    if (window.matchMedia("(max-width: 920px)").matches === true) {
        if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {
            $("nav").css("position", "relative");
        } else {
            $("nav").css("position", "fixed");
        }

        if ((window.innerHeight + Math.round(window.scrollY)) >= document.body.offsetHeight) {
            $(".nav_links").css("bottom", "-300px");
        } else {
            $(".nav_links").css("bottom", "0px");
        }
    } else {
        if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {
            $("nav").css("background-color", "var(--dark)");
            $("nav").css("box-shadow", "0px 6px 16px -6px var(--gray)");
        } else {
            $("nav").css("background-color", "transparent");
            $("nav").css("box-shadow", "none");
        }
    }
}


$(".lang").on("click", function () {
    if ($(this).hasClass("en")) {
        $(this).html('<iconify-icon icon="material-symbols:language-spanish-rounded"></iconify-icon>');
        $(this).removeClass("en").addClass("es");
    } else {
        $(this).html('<iconify-icon icon="ri:english-input"></iconify-icon>');
        $(this).removeClass("es").addClass("en");
    }
});


Number.prototype.format = function (n) {
    var r = new RegExp('\\d(?=(\\d{3})+' + (n > 0 ? '\\.' : '$') + ')', 'g');
    return this.toFixed(Math.max(0, Math.floor(n))).replace(r, '$&,');
};

$('.count').each(function () {
    $(this).prop('counter', 0).animate({
        counter: $(this).text()
    }, {
        duration: 10000,
        easing: 'easeOutExpo',
        step: function (step) {
            $(this).text('' + step.format());
        }
    });
});

