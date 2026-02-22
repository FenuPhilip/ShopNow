// ShopNow Main JS

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    });
  }, 5000);

  // Quantity input +/- button helpers (for product detail)
  document.querySelectorAll('.qty-input').forEach(input => {
    const dec = input.previousElementSibling;
    const inc = input.nextElementSibling;
    if (dec) dec.addEventListener('click', () => {
      if (parseInt(input.value) > 1) input.value = parseInt(input.value) - 1;
    });
    if (inc) inc.addEventListener('click', () => {
      const max = parseInt(input.getAttribute('max') || 9999);
      if (parseInt(input.value) < max) input.value = parseInt(input.value) + 1;
    });
  });

  // Highlight selected address card
  document.querySelectorAll('.address-select').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.address-select').forEach(c => {
        c.classList.remove('border-warning');
        c.style.background = '';
      });
      card.classList.add('border-warning');
      card.style.background = '#fff3cd';
    });
  });
});
