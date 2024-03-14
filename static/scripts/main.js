// Define a Message class to encapsulate message creation and rendering
class Message {
    constructor(text, side) {
        this.text = text;
        this.messageSide = side;
    }

    draw() {
        const $message = $($('.message_template').clone().html());
        $message.addClass(this.messageSide).find('.text').html(this.text);

        const url = this.messageSide === 'left' ? '/static/images/bot.png' : '/static/images/user.png';
        $message.find('.avatar').css('background-image', `url(${url})`);

        $('.messages').append($message);
        setTimeout(() => $message.addClass('appeared'), 0);
    }
}

// Function to send a message
function sendMessage(text) {
    if (text.trim() === '') return;

    $('.message_input').val('');
    const $messages = $('.messages');
    const message = new Message(text, 'right');
    message.draw();
    $messages.stop().animate({scrollTop: $messages.prop('scrollHeight')}, 700);

    $.ajax({
        type: 'GET',
        url: '/get_response',
        data: {
            user_input: text,
        },
        success: function (response) {
            const messagesList = JSON.parse(response);
            messagesList.forEach(msg => {
                const message = new Message(msg, 'left');
                message.draw();
            });
            $messages.stop().animate({scrollTop: $messages.prop('scrollHeight')}, 700);
        }
    });

}

// Function to get message text from input field
function getMessageText() {
    return $('.message_input').val();
}

// Event listeners for sending message on button click and pressing Enter key
$(function () {
    $('.send_message').click(() => sendMessage(getMessageText()));
    $('.message_input').keyup(function (e) {
        if (e.which === 13) sendMessage(getMessageText());
    });

    // Display initial greeting message
});
const greetingMessage = new Message('Hi, I am a simple bot. How can I help you?', 'left');

// Function to display SweetAlert prompt
function showNamePrompt() {
    Swal.fire({
        title: 'Enter your name',
        input: 'text',
        inputPlaceholder: 'Your name',
        showCancelButton: true,
        confirmButtonText: 'Submit',
        cancelButtonText: 'Cancel',
        allowOutsideClick: false
    }).then((result) => {
        if (result.isConfirmed) {
            const name = result.value;
            if (name.trim() !== '') {
                $.ajax({
                    type: 'GET',
                    url: '/set_username',
                    data: {
                        username: name,
                    },
                    success: function () {
                        // Process the user's name (you can send it to the server or do something else)
                        greetingMessage.draw();
                    }
                });

            } else {
                // If the user didn't enter a name, show an error message
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: 'You must enter your name!',
                    allowOutsideClick: false
                }).then(() => {
                    // Show the prompt again
                    showNamePrompt();
                });
            }
        } else {
            Swal.fire({
                icon: 'info',
                title: 'sure',
                text: 'Your temporary name is user!',
                allowOutsideClick: false
            }).then(() => {
                $.ajax({
                    type: 'GET',
                    url: '/set_username',
                    data: {
                        username: 'user',
                    },
                    success: function () {
                        // Process the user's name (you can send it to the server or do something else)
                        greetingMessage.draw();
                    }
                });

            })
        }
    });
}


// Function to fetch chat history using AJAX
function fetchChatHistory() {
    $.ajax({
        type: 'GET',
        url: '/get_chat_history',
        success: function (response) {
            if (response.length > 0) {
            // Display the chat history
            displayChatHistory(response);
            }
            else {

                        // Process the user's name (you can send it to the server or do something else)
                        greetingMessage.draw();
            }
        },
        error: function (xhr, status, error) {
            console.error('Error fetching chat history:', error);
        }
    });
}

// Function to display chat history
function displayChatHistory(chatHistory) {
    chatHistory.forEach(function (item) {
        var who = item['who']; // Access the 'who' key
        var messageText = item['message']; // Access the 'message' key

        // Determine the message side based on who sent the message
        var messageSide = (who === 'Chatbot') ? 'left' : 'right';

        // Create a new Message object with the message text and message side
        var message = new Message(messageText, messageSide);

        // Draw the message
        message.draw();
    });

    // Scroll to the bottom of the chat history
    var $messages = $('.messages');
    $messages.stop().animate({scrollTop: $messages.prop('scrollHeight')}, 700);
}

// Call the function to show the prompt when the page loads
window.addEventListener('load', function () {
    // Check if currentUser is undefined
    if (currentUser === '') {
        // Show the prompt only if currentUser is undefined
        showNamePrompt();
    } else {
        // Display the chat history if currentUser is defined
        fetchChatHistory();
    }
});


// Add event listener to the Clear Chat button
function clearChatHistory() {
    // Clear the chat history in the UI
    $('.messages').empty();

    // Optionally, clear the chat history in the backend using AJAX
    $.ajax({
        type: 'POST',
        url: '/clear_chat_history',
        success: function (response) {
            Swal.fire({
                icon: 'success',
                title: 'All Clear',
                text: 'Chat history cleared successfully!',
                allowOutsideClick: false,
                showConfirmButton: false
                , timer: 1500, timerProgressBar: true,
            }).then(() => {

                        // Process the user's name (you can send it to the server or do something else)
                        greetingMessage.draw();



            })
            console.log('Chat history cleared successfully.');
        },
        error: function (xhr, status, error) {
            console.error('Error clearing chat history:', error);
        }
    });
}
