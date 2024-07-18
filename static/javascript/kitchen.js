let currentOrderId = null;

function showOrderModal(orderId) {
  currentOrderId = orderId;
  fetch(`/orders/${orderId}`)
    .then(response => response.json())
    .then(order => {
      const modalBody = document.querySelector('.modal-body');
      modalBody.innerHTML = `
        <div class="row justify-content-between">
          <div class="col-md-9"><h5 class="card-title">Mesa ${order.table_number} </h5></div>
          <div class="col-md-3"><span class="badge bg-primary">Prioridad ${order.priority}</span></div> 
        </div>
        <p>Hora del Pedido: ${order.order_time}</p>
        
        <h6>Items:</h6>
        <ul>
          ${order.items.map(item => `<li>${item.quantity} x ${item.name} </li>`).join('')}
        </ul>
      `;
      const orderModal = new bootstrap.Modal(document.getElementById('orderModal'));
      orderModal.show();
    });
}

function completeOrder() {
  if (currentOrderId) {
    fetch('/orders/update_status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ order_id: currentOrderId })
    }).then(response => response.json())
      .then(data => {
        if (data.success) {
          alertify.success('Pedido marcado como completado');
          window.location.reload();
        } else {
          alertify.error('Hubo un problema al marcar el pedido como completado');
        }
      });
  }
}
