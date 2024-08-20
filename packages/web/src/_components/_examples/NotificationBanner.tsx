import React, { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

type NotificationType = "success" | "error" | "info";

interface Notification {
  id: string;
  message: string;
  type: NotificationType;
  timeout: number;
}

const NotificationSystem: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (message: string, type: NotificationType, timeout = 5000) => {
    const newNotification: Notification = { id: uuidv4(), message, type, timeout };
    setNotifications((prev) => [...prev, newNotification]);

    setTimeout(() => {
      removeNotification(newNotification.id);
    }, timeout);
  };

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((notif) => notif.id !== id));
  };

  const getTypeStyles = (type: NotificationType) => {
    switch (type) {
      case "success":
        return "bg-green-500 text-white";
      case "error":
        return "bg-red-500 text-white";
      case "info":
        return "bg-blue-500 text-white";
      default:
        return "";
    }
  };

  return (
    <div className="fixed top-4 right-4 space-y-2 z-50">
      {notifications.map((notif) => (
        <div
          key={notif.id}
          className={`p-4 rounded-md shadow-lg transition transform hover:scale-105 ${getTypeStyles(
            notif.type
          )}`}
        >
          <p>{notif.message}</p>
        </div>
      ))}
      <div className="space-x-2">
        <button
          className="bg-green-500 text-white p-2 rounded"
          onClick={() => addNotification("Success notification", "success")}
        >
          Trigger Success
        </button>
        <button
          className="bg-red-500 text-white p-2 rounded"
          onClick={() => addNotification("Error notification", "error")}
        >
          Trigger Error
        </button>
        <button
          className="bg-blue-500 text-white p-2 rounded"
          onClick={() => addNotification("Info notification", "info")}
        >
          Trigger Info
        </button>
      </div>
    </div>
  );
};

export default NotificationSystem;
