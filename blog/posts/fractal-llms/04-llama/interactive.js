document.addEventListener('DOMContentLoaded', function() {
    const collapsibleTriggers = document.querySelectorAll('.collapsible-trigger');
  
    collapsibleTriggers.forEach(function(trigger) {
      trigger.addEventListener('click', function() {
        this.classList.toggle('active');
        const content = this.nextElementSibling;
        if (content.style.display === 'block') {
          content.style.display = 'none';
        } else {
          content.style.display = 'block';
        }
      });
    });
  });