// Constants for fare calculation
const BASE_FARE = 100; // Base fare in PKR
const PER_KM_RATE = 15; // Rate per kilometer
const PER_MINUTE_RATE = 2; // Rate per minute
const SURGE_MULTIPLIER = 1.5; // Surge pricing multiplier
const MIN_FARE = 150; // Minimum fare

// Check if it's surge pricing time (peak hours)
const isSurgePricing = () => {
  const now = new Date();
  const hour = now.getHours();
  
  // Define peak hours (e.g., morning rush 7-10 AM and evening rush 4-8 PM)
  const isPeakMorning = hour >= 7 && hour <= 10;
  const isPeakEvening = hour >= 16 && hour <= 20;
  
  return isPeakMorning || isPeakEvening;
};

// Calculate demand-based surge multiplier
const calculateDemandMultiplier = (activeRides, availableDrivers) => {
  if (!availableDrivers) return 1;
  const ratio = activeRides / availableDrivers;
  
  if (ratio > 0.8) return SURGE_MULTIPLIER;
  if (ratio > 0.6) return 1.3;
  if (ratio > 0.4) return 1.2;
  return 1;
};

/**
 * Calculate the fare for a ride
 * @param {number} distance - Distance in meters
 * @param {number} duration - Duration in seconds
 * @param {number} activeRides - Number of active rides in the area
 * @param {number} availableDrivers - Number of available drivers in the area
 * @returns {number} - Total fare in PKR
 */
export const calculateFare = (
  distance,
  duration,
  activeRides = 0,
  availableDrivers = 1
) => {
  // Convert distance to kilometers and duration to minutes
  const distanceKm = distance / 1000;
  const durationMinutes = duration / 60;

  // Calculate base components
  const distanceFare = distanceKm * PER_KM_RATE;
  const timeFare = durationMinutes * PER_MINUTE_RATE;
  let totalFare = BASE_FARE + distanceFare + timeFare;

  // Apply surge pricing if applicable
  if (isSurgePricing()) {
    const demandMultiplier = calculateDemandMultiplier(activeRides, availableDrivers);
    totalFare *= demandMultiplier;
  }

  // Apply minimum fare
  totalFare = Math.max(totalFare, MIN_FARE);

  // Round to nearest rupee
  return Math.round(totalFare);
};

/**
 * Calculate the estimated time of arrival (ETA)
 * @param {number} distance - Distance in meters
 * @param {number} trafficFactor - Traffic congestion factor (1 = normal, >1 = heavy traffic)
 * @returns {number} - ETA in minutes
 */
export const calculateETA = (distance, trafficFactor = 1) => {
  const averageSpeed = 30; // Average speed in km/h
  const distanceKm = distance / 1000;
  
  // Calculate basic ETA
  let eta = (distanceKm / averageSpeed) * 60; // Convert to minutes
  
  // Apply traffic factor
  eta *= trafficFactor;
  
  return Math.round(eta);
};

/**
 * Format fare for display
 * @param {number} fare - Fare amount in PKR
 * @returns {string} - Formatted fare string
 */
export const formatFare = (fare) => {
  return `Rs. ${fare.toLocaleString()}`;
}; 