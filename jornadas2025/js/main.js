(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();
    
    const originalLogo = "../../img/logos/Logo-JFP-2025-invertido-transparente.png";
    const scrolledLogo = "../../img/logos/JFP2025-LOGO-TRANSPARENTE.png";
    
    function updateNavbarLogo() {
        const scrollTop = $(window).scrollTop();
        const windowWidth = $(window).width();
    
        if (scrollTop > 45) {
            $('.navbar').addClass('sticky-top');
            $('.navbar-logo').attr('src', scrolledLogo);
        } else {
            $('.navbar').removeClass('sticky-top');
            if (windowWidth < 992) {
                $('.navbar-logo').attr('src', scrolledLogo);
            } else {
                $('.navbar-logo').attr('src', originalLogo);
            }
        }
    }
    

    $(document).ready(function () {
        updateNavbarLogo();
    });

    $(window).on('scroll resize', function () {
        updateNavbarLogo();
    });


    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').scrollTop(0);
        return false;
    });


    // Modal Video
    var $videoSrc;
    $('.btn-play').click(function () {
        $videoSrc = $(this).data("src");
    });
    console.log($videoSrc);
    $('#videoModal').on('shown.bs.modal', function (e) {
        $("#video").attr('src', $videoSrc + "?autoplay=1&amp;modestbranding=1&amp;showinfo=0");
    })
    $('#videoModal').on('hide.bs.modal', function (e) {
        $("#video").attr('src', $videoSrc);
    })


    // Project and Testimonial carousel
    $(".project-carousel, .testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 25,
        loop: true,
        center: true,
        dots: false,
        nav: true,
        navText : [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ],
        responsive: {
			0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });
    // Leer más funcionalidad
    $('.read-more-btn').click(function () {
        const description = $(this).prev('.description');
        description.toggleClass('expanded');
        $(this).text(description.hasClass('expanded') ? 'Leer menos' : 'Leer más');
    });
})(jQuery);
