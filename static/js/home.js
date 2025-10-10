let menu = document.getElementById('dropdownMenu');

if (menu){
  function toggleMenu() {
      menu.classList.toggle('hidden');
  }
      
}

/*
  // Optional: close dropdown if click outside
  document.addEventListener('click', function (e) {
    const menu = document.getElementById('dropdownMenu');
    const profile = document.querySelector('.profile-pic');
    if (!profile.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.add('hidden');
    }
  });
*/