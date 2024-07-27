// Function to toggle dark mode for the body and background color for other elements
function toggleTheme() {
  const isChecked = document.getElementById('theme-switch').checked;
  const newMode = isChecked ? 'dark' : 'light';
  const bgClassToAdd = isChecked ? 'dark-mode' : 'light-mode';
  const bgClassToRemove = isChecked ? 'light-mode' : 'dark-mode';

  // Toggle the theme on the body element
  document.body.classList.toggle('dark-mode', isChecked);
  document.body.classList.toggle('light-mode', !isChecked);

  // Apply the background color class to elements with specified class names
  applyBackgroundColor('chat_window', bgClassToAdd, bgClassToRemove);
  applyBackgroundColor('message_input', bgClassToAdd, bgClassToRemove);

  // Save the new mode to local storage
  localStorage.setItem('theme', newMode);
}

// Function to apply background color classes to elements with specific class names
function applyBackgroundColor(className, addClass, removeClass) {
  const elements = document.getElementsByClassName(className);
  Array.from(elements).forEach(element => {
    element.classList.add(addClass);
    element.classList.remove(removeClass);
  });
}

// Function to initialize theme and background color based on local storage
function initializeTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  const isDarkMode = savedTheme === 'dark';
  const bgClassToAdd = isDarkMode ? 'dark-mode' : 'light-mode';
  const bgClassToRemove = isDarkMode ? 'light-mode' : 'dark-mode';

  // Set initial theme on the body element
  document.body.classList.add(isDarkMode ? 'dark-mode' : 'light-mode');
  document.body.classList.remove(isDarkMode ? 'light-mode' : 'dark-mode');

  // Apply the background color class to elements with specified class names
  applyBackgroundColor('chat_window', bgClassToAdd, bgClassToRemove);
  applyBackgroundColor('message_input', bgClassToAdd, bgClassToRemove);

  // Set checkbox state
  document.getElementById('theme-switch').checked = isDarkMode;
}

// Add event listener to the checkbox
document.getElementById('theme-switch').addEventListener('change', toggleTheme);

// Initialize the theme and colors when the page loads
initializeTheme();
