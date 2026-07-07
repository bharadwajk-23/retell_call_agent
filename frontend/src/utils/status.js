import { BOOKING_STATUS } from '../constants/config'

// Maps a patient's booking_status (from the API) to button label/variant.
export function getBookingStatusMeta(bookingStatus) {
  const status = bookingStatus || BOOKING_STATUS.NOT_BOOKED

  switch (status) {
    case BOOKING_STATUS.IN_PROGRESS:
      return { status, label: 'Calling…', variant: 'in-progress', disabled: true }
    case BOOKING_STATUS.BOOKED:
      return { status, label: 'Booked', variant: 'booked', disabled: true }
    default:
      return { status, label: 'Start Call', variant: 'not-booked', disabled: false }
  }
}
