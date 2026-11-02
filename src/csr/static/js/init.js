// Initialises the design system components the site uses (specification 6.2).
import DS from '../vendor/sgds/4.3.0/design-system.js';

document.documentElement.classList.add('js-enabled');

const mobileNavigation = document.querySelector('[data-module="ds-mobile-navigation-menu"]');
if (mobileNavigation) {
  new DS.components.SiteNavigation(mobileNavigation).init();
}

DS.components.skipLinks.init();

document.querySelectorAll('[data-module="ds-details"]').forEach((element) => {
  new DS.components.Details(element).init();
});
