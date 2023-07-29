$(document).ready(function() {
    $('.accept-btn').click(function(e) {
      e.preventDefault();
      var requestId = $(this).data('request-id');
      var cardElement = $(this).closest('.card');
      acceptFriendRequest(requestId, cardElement);
    });
  
    function acceptFriendRequest(requestId, cardElement) {
      var url = '/accept_friend_request/' + requestId + '/';
      var data = {
        csrfmiddlewaretoken: '{{ csrf_token }}'
      };
  
      $.post(url, data)
        .done(function(response) {
          if (response.success) {
            updateUIAfterAccept(cardElement);
          } else {
            alert('Failed to accept friend request.');
          }
        })
        .fail(function(xhr, status, error) {
          console.log(error);
          alert('An error occurred.');
        });
    }
  
    function updateUIAfterAccept(cardElement) {
      var acceptBtn = cardElement.find('.accept-btn');
      var rejectBtn = cardElement.find('.reject-btn');
  
      acceptBtn.text('Accepted');
      acceptBtn.attr('disabled', true);
      rejectBtn.remove();
    }
  });
  