// Configuration globale
const CONFIG = {
  alertTimeout: 3000,
  animationThreshold: 0.15,
  cardRevealTrigger: 0.85
};

// Initialisation principale
document.addEventListener("DOMContentLoaded", function() {
  initAnimations();
  initContactForm();
  initSmoothScroll();
  initAlerts();
  
  // Initialisation spécifique à la page projets
  if (document.querySelector('.project-item')) {
    initProjectPage();
  }
});

// Fonction d'initialisation des animations
function initAnimations() {
  const faders = document.querySelectorAll('.fade-in, .slide-in, .bounce-in');
  if (!faders.length) return;

  const appearOptions = { 
    threshold: CONFIG.animationThreshold,
    rootMargin: '0px 0px -50px 0px'
  };

  const appearOnScroll = new IntersectionObserver(function(entries, observer) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('appear');
        observer.unobserve(entry.target);
      }
    });
  }, appearOptions);

  faders.forEach(fader => {
    appearOnScroll.observe(fader);
  });
}

// Fonction d'initialisation du formulaire de contact
function initContactForm() {
  const contactForm = document.getElementById("contactForm");
  if (!contactForm) return;

  contactForm.addEventListener("submit", function(e) {
    const btn = this.querySelector("button[type=submit]");
    if (!btn) return;

    const originalText = btn.innerText;
    
    btn.classList.add("btn-warning");
    btn.innerText = "Envoi...";
    btn.disabled = true;

    // Réinitialiser après délai (simulation)
    setTimeout(() => {
      btn.innerText = originalText;
      btn.classList.remove("btn-warning");
      btn.disabled = false;
    }, 2000);
  });
}

// Fonction pour le smooth scroll
function initSmoothScroll() {
  const navLinks = document.querySelectorAll('a.nav-link[href^="#"]');
  if (!navLinks.length) return;

  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const targetElement = document.querySelector(href);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
        
        // Mise à jour de l'URL (optionnel)
        history.pushState(null, null, href);
      }
    });
  });
}

// Fonction pour la disparition des alertes
function initAlerts() {
  const alerts = document.querySelectorAll('.alert');
  if (!alerts.length) return;

  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";
      
      setTimeout(function() {
        if (alert.parentNode) {
          alert.remove();
        }
      }, 500);
    }, CONFIG.alertTimeout);
  });
}

// Fonctions spécifiques à la page projets
function initProjectPage() {
  initProjectFilter();
  initProjectReveal();
  initLightbox();
}

function initProjectFilter() {
  const filterBtns = document.querySelectorAll(".filter-btn");
  const projects = document.querySelectorAll(".project-item");
  
  if (!filterBtns.length || !projects.length) return;

  function filterProjects(category) {
    projects.forEach(project => {
      if (category === "all" || project.classList.contains(category)) {
        project.style.display = "block";
        setTimeout(() => project.classList.add("show"), 10);
      } else {
        project.classList.remove("show");
        setTimeout(() => project.style.display = "none", 300);
      }
    });
  }

  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const currentActive = document.querySelector(".filter-btn.active");
      if (currentActive) {
        currentActive.classList.remove("active");
      }
      btn.classList.add("active");
      filterProjects(btn.getAttribute("data-filter"));
    });
  });

  // Activer "all" par défaut
  const allBtn = document.querySelector('.filter-btn[data-filter="all"]');
  if (allBtn) {
    allBtn.classList.add('active');
  }
  filterProjects("all");
}

function initProjectReveal() {
  const cards = document.querySelectorAll(".animate-card");
  if (!cards.length) return;

  function revealCards() {
    const triggerBottom = window.innerHeight * CONFIG.cardRevealTrigger;
    
    cards.forEach(card => {
      const cardTop = card.getBoundingClientRect().top;
      if (cardTop < triggerBottom) {
        card.classList.add("show");
      }
    });
  }

  // Utiliser Intersection Observer pour une meilleure performance
  if ('IntersectionObserver' in window) {
    const cardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('show');
          cardObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    cards.forEach(card => {
      cardObserver.observe(card);
    });
  } else {
    // Fallback pour les navigateurs plus anciens
    window.addEventListener("scroll", revealCards);
    revealCards(); // Vérifier immédiatement
  }
}

function initLightbox() {
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const caption = document.getElementById("lightbox-caption");
  const closeBtn = document.querySelector(".lightbox-close");
  const triggers = document.querySelectorAll(".lightbox-trigger");

  if (!lightbox || !triggers.length) return;

  function openLightbox(src, title) {
    // Vérifier si l'image existe avant d'ouvrir la lightbox
    if (!src) {
      console.error("Source d'image manquante");
      return;
    }
    
    // Précharger l'image pour vérifier qu'elle existe
    const testImage = new Image();
    testImage.onload = function() {
      if (lightboxImg) lightboxImg.src = src;
      if (caption) caption.textContent = title || '';
      lightbox.style.display = "block";
      document.body.style.overflow = "hidden";
    };
    testImage.onerror = function() {
      console.error("Image non trouvée:", src);
      alert("L'image n'est pas disponible pour le moment.");
    };
    testImage.src = src;
  }

  function closeLightbox() {
    lightbox.style.display = "none";
    document.body.style.overflow = "";
  }

  triggers.forEach(trigger => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault(); // Empêcher le comportement par défaut
      const src = trigger.src || trigger.getAttribute('data-src') || trigger.getAttribute('href');
      const title = trigger.getAttribute("data-title") || trigger.alt || trigger.title;
      
      // Vérifier que nous avons une source valide
      if (src && src !== '#') {
        openLightbox(src, title);
      } else {
        console.error("Source d'image invalide:", src);
      }
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", closeLightbox);
  }

  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox.style.display === "block") {
      closeLightbox();
    }
  });
}

document.addEventListener("DOMContentLoaded", function() {
  const images = document.querySelectorAll('img');
  images.forEach(img => {
    img.onerror = function() {
      console.error(`Image non trouvée: ${this.src}`);
      this.style.display = 'none';
      // Optionnel: afficher un placeholder
      const placeholder = document.createElement('div');
      placeholder.className = 'image-placeholder';
      placeholder.textContent = 'Image non disponible';
      this.parentNode.insertBefore(placeholder, this.nextSibling);
    };
  });
});


