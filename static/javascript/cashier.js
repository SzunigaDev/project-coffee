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
  const printWindow = window.open('', '', 'width=400,height=600');
  printWindow.document.write('<html><head><title>Ticket de Venta</title>');
  printWindow.document.write('<style>body{font-family:"Courier New",Courier,monospace;max-width:400px;margin:auto;border:1px solid #000;padding:20px}.header,.footer{text-align:center;margin-bottom:20px}.header h2,.header h3,.footer p{margin:5px 0}.content{border-top:1px dashed #000;border-bottom:1px dashed #000;padding:10px 0}.content table{width:100%}.content table,.content th,.content td{border:none;border-collapse:collapse;text-align:left}.content th,.content td{padding:5px 0}.total{text-align:right;margin-top:10px}.barcode{text-align:center;margin-top:20px}</style>');
  printWindow.document.write('</head><body>');
  printWindow.document.write('<div class="header">');
  printWindow.document.write('<h2>Mi Cafetería Feliz</h2>');
  printWindow.document.write('<p>RFC: ABC-123456-XYZ</p>');
  printWindow.document.write('<p>Fecha: ' + ticketContent.order_time + '</p>');
  printWindow.document.write('<p>Factura No: ' + String(ticketContent.id).padStart(10, '0') + '</p>');
  printWindow.document.write('<p>Av. Ficticia 123, Ciudad, País</p>');
  printWindow.document.write('<p>TEL: 123-456-7890</p>');
  printWindow.document.write('</div>');
  printWindow.document.write('<div class="content">');
  printWindow.document.write('<table>');
  printWindow.document.write('<thead><tr><th>CANT</th><th>DESCRIPCIÓN</th><th>PRECIO</th><th>IMPORTE</th></tr></thead>');
  printWindow.document.write('<tbody>');
  ticketContent.items.forEach(item => {
      printWindow.document.write('<tr><td>' + item.quantity + '</td><td>' + item.name + '</td><td>' + item.price.toFixed(2) + '</td><td>' + (item.price * item.quantity).toFixed(2) + '</td></tr>');
  });
  printWindow.document.write('</tbody></table></div>');
  printWindow.document.write('<div class="total"><p>Total Neto: $' + ticketContent.total_amount.toFixed(2) + '</p>');
  printWindow.document.write('<p>Pago: $' + ticketContent.payment_amount.toFixed(2) + '</p>');
  printWindow.document.write('<p>Cambio: $' + ticketContent.change_amount.toFixed(2) + '</p>');
  printWindow.document.write('</div>');
  printWindow.document.write('<div class="footer">');
  printWindow.document.write('<p>Vendedor: ' + ticketContent.user_id + '</p>');
  printWindow.document.write('<p>Folio Interno: ' + String(ticketContent.id).padStart(10, '0')  + '</p>');
  printWindow.document.write('<p>¡Gracias por su compra!</p>');
  printWindow.document.write('</div>');
  printWindow.document.write('<div class="barcode">');
  printWindow.document.write('<img src="https://barcode.tec-it.com/barcode.ashx?data=' + String(ticketContent.id).padStart(10, '0') + '&code=Code128" alt="Código de Barras">');
  printWindow.document.write('</div>');
  printWindow.document.write('<div class="payment">');
  printWindow.document.write('</div>');
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
        'id':order.id,
        'table_number': order.table_number,
        'order_time': order.order_time,
        'total_amount': order.total_amount,
        'items': order.items,
        'payment_amount': order.payment_amount,
        'change_amount': order.change,
        'user_id': order.user_id
      };
      printTicket(ticketContent);
    });
}
