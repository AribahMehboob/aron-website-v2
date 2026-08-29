/**
 * ARON Component Loader & Active Link Highlighter
 * Loads modular components (navbar, footer, reviews, previous-events, chatbot) dynamically
 */

document.addEventListener('DOMContentLoaded', async () => {
  const includes = document.querySelectorAll('[data-include]');
  
  const loadTasks = Array.from(includes).map(async (el) => {
    const file = el.getAttribute('data-include');
    try {
      const response = await fetch(file);
      if (response.ok) {
        const html = await response.text();
        el.outerHTML = html;
      } else {
        console.error(`Failed to load component: ${file}`);
      }
    } catch (err) {
      console.error(`Error fetching component ${file}:`, err);
    }
  });

  await Promise.all(loadTasks);

  // 1. Highlight Active Nav Link based on current page
  highlightActiveNav();

  // 2. Initialize Mobile Drawer Listeners
  initMobileDrawer();

  // 3. Initialize Chatbot Script if present
  if (typeof initChatbot === 'function') {
    initChatbot();
  }
});

function highlightActiveNav() {
  let path = window.location.pathname.split('/').pop().replace('.html', '');
  if (!path || path === '' || path === '/') path = 'index';

  // Desktop & Mobile Drawer Links
  const links = document.querySelectorAll('.navlinks a[data-page], .drawer-nav a[data-page]');
  links.forEach((link) => {
    const pageAttr = link.getAttribute('data-page');
    if (pageAttr === path) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

function initMobileDrawer() {
  const burger = document.getElementById('burger');
  const drawer = document.getElementById('drawer');
  const drawerClose = document.getElementById('drawerClose');
  const drawerOverlay = document.getElementById('drawerOverlay');

  if (!burger || !drawer) return;

  function openDrawer() {
    drawer.classList.add('open');
    if (drawerOverlay) drawerOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer.classList.remove('open');
    if (drawerOverlay) drawerOverlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  burger.addEventListener('click', openDrawer);
  if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
  if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);
}
