export function unixToDate(unix: number) {
    const date = new Date(unix)
    const newDate = date.toLocaleString()
    return newDate
} 