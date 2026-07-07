// Mirrors the booking_status → label/variant mapping from the legacy app.js.
export function getBookingStatusMeta(bookingStatus) {
  const status = bookingStatus || 'not booked'

  switch (status) {
    case 'in progress':
      return { status, label: 'Calling…', variant: 'in-progress', disabled: true }
    case 'booked':
      return { status, label: 'Booked', variant: 'booked', disabled: true }
    default:
      return { status, label: 'Start Call', variant: 'not-booked', disabled: false }
  }
}
