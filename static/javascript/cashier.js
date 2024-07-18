let currentOrderId = null;

function showOrderDetails(orderId) {
  currentOrderId = orderId;
  fetch(`/orders/${orderId}`)
    .then(response => response.json())
    .then(order => {
      if (order.error) {
        alertify.error('Pedido no encontrado');
        return;
      }
      const orderDetails = document.getElementById('order-details');
      orderDetails.innerHTML = `
        <h5 class="card-title">Mesa ${order.table_number}</h5>
        <p>Hora del Pedido: ${order.order_time}</p>
        <h6>Platillos:</h6>
        <ul>
          ${order.items.map(item => `<li>${item.quantity} x ${item.name} - $${item.price}</li>`).join('')}
        </ul>
        <p>Total: $${order.total_amount}</p>
      `;
      const showHideElement = document.getElementById('show-hide');
      
      if (order.status === 'Pagado') {
        orderDetails.innerHTML += `<button class="btn btn-info" onclick="reprintTicket(${order.id})">Reimprimir Ticket</button>`;
        showHideElement.style.display = 'none';
      } else {
        showHideElement.style.display = 'block';
      }

      document.getElementById('order-total').value = order.total_amount;
      if (order.payment_amount !== null && order.change !== null) {
        document.getElementById('payment-amount').value = order.payment_amount;
      } else {
        document.getElementById('payment-amount').value = 0;
      }
    });
}

function calculateChange() {
  const total = parseFloat(document.getElementById('order-total').value);
  const paymentAmount = parseFloat(document.getElementById('payment-amount').value);
  if (!isNaN(total) && !isNaN(paymentAmount)) {
    const change = paymentAmount - total;
    document.getElementById('change-amount').value = change.toFixed(2); 
  }
}

function completeOrder() {
  const paymentAmount = parseFloat(document.getElementById('payment-amount').value);
  if (currentOrderId && paymentAmount) {
    fetch('/orders/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ order_id: currentOrderId, payment_amount: paymentAmount })
    }).then(response => response.json())
      .then(data => {
        if (data.success) {
          alertify.success('Pedido cobrado con éxito');
          printTicket(data.ticket_content);
          window.location.reload();
        } else {
          alertify.error('Hubo un problema al cobrar el pedido');
        }
      });
  } else {
    alertify.error('Por favor seleccione un pedido y especifique el monto con el que pagan');
  }
}

function printTicket(ticketContent) {
  const printWindow = window.open('', '', 'width=600,height=400');
  printWindow.document.write('<html><head><title>Ticket</title></head><body>');
  printWindow.document.write('<h1>Ticket de Venta</h1>');
  printWindow.document.write(`<p>Mesa: ${ticketContent.table_number}</p>`);
  printWindow.document.write(`<p>Hora del Pedido: ${ticketContent.order_time}</p>`);
  printWindow.document.write('<h2>Platillos:</h2>');
  printWindow.document.write('<ul>');
  ticketContent.items.forEach(item => {
    printWindow.document.write(`<li>${item.quantity} x ${item.name} - $${item.price}</li>`);
  });
  printWindow.document.write('</ul>');
  printWindow.document.write(`<p>Total: $${ticketContent.total_amount}</p>`);
  printWindow.document.write(`<p>Pago: $${ticketContent.payment_amount}</p>`);
  printWindow.document.write(`<p>Cambio: $${ticketContent.change.toFixed(2)}</p>`);
  printWindow.document.write('</body></html>');
  printWindow.document.close();
  printWindow.print();
}

function reprintTicket(orderId) {
  fetch(`/orders/${orderId}`)
    .then(response => response.json())
    .then(order => {
      if (order.error) {
        alertify.error('Pedido no encontrado');
        return;
      }
      const ticketContent = {
        'table_number': order.table_number,
        'order_time': order.order_time,
        'total_amount': order.total_amount,
        'items': order.items,
        'payment_amount': order.payment_amount,
        'change': order.change
      };
      printTicket(ticketContent);
    });
}
