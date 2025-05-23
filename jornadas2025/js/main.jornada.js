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


    const originalLogo = "../img/logos/Logo-JFP-2025-invertido-transparente.png";
    const scrolledLogo = "../img/logos/JFP2025-LOGO-TRANSPARENTE.png";
    
    function updateNavbarLogo() {
        const scrollTop = $(window).scrollTop();
        const windowWidth = $(window).width();
    
        if (scrollTop > 45) {
            $('.navbar').addClass('sticky-top shadow-sm');
            $('#navbar-logo').attr('src', scrolledLogo);
        } else {
            $('.navbar').removeClass('sticky-top shadow-sm');
            // Si es mobile (menor a 992px), muestro logo con letras azules
            if (windowWidth < 992) {
                $('#navbar-logo').attr('src', scrolledLogo);
            } else {
                $('#navbar-logo').attr('src', originalLogo);
            }
        }
    }
    
    $(document).ready(function () {
        updateNavbarLogo(); // Ejecuta una vez al cargar
    });
    
    $(window).on('scroll resize', function () {
        updateNavbarLogo(); // Actualiza al hacer scroll o redimensionar
    });


    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').scrollTop(0);
        return false;
    });


    // Facts counter
    $('[data-toggle="counter-up"]').counterUp({
        delay: 10,
        time: 2000
    });


    // Screenshot carousel
    $(".screenshot-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        loop: true,
        dots: true,
        items: 1
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
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
        const description = $(this).prev('.description-magistral');
        description.toggleClass('expanded');
        $(this).text(description.hasClass('expanded') ? 'Leer menos' : 'Leer más');
    });
})(jQuery);

