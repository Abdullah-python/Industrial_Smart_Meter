from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Meter, MeterAssignment, MeterData
from .serializers import MeterSerializer, MeterAssignmentSerializer, MeterDataSerializer
from accounts.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone
import os

class MeterViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing meters.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    lookup_field = 'device_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "details": {
                    "message": "Meter retrieved successfully",
                    "data": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "error": "Error retrieving meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            print("Received POST request:", request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "details": {
                    "message": "Meter created successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": "Error creating meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            device_id = instance.device_id
            self.perform_destroy(instance)
            return Response({
                "details": {
                    "message": f"Meter with device ID '{device_id}' was successfully deleted"
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error deleting meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "details": {
                    "message": "Meter updated successfully",
                    "data": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "error": "Error updating meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        """Custom perform_update method"""
        serializer.save()


class MeterAssignmentViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            assignments = MeterAssignment.objects.all()
            serializer = MeterAssignmentSerializer(assignments, many=True)
            return Response({
                "details": {
                    "message": "Meter assignments retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving meter assignments",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        serializer = MeterAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                assignment = serializer.save()
                return Response({
                    "details": {
                        "message": "Meter assignment created successfully",
                        "data": MeterAssignmentSerializer(assignment).data
                    }
                }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({
                    "error": "Validation error",
                    "details": e.message_dict if hasattr(e, 'message_dict') else {"detail": list(e)}
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "error": "Error creating meter assignment",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            assignment_id = pk
            if not assignment_id:
                return Response({
                    "error": "Assignment ID is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            assignment = MeterAssignment.objects.get(id=assignment_id)
            assignment.delete()
            return Response(
                {
                    "details": {
                        "message": "Meter assignment deleted successfully"
                    }
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error deleting meter assignment",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeterDataViewSet(viewsets.ViewSet):
    """
    API endpoints for managing meter data.
    """

    def list(self, request):
        """Get all meter data or filter by meter_id"""
        try:
            meter_id = request.query_params.get('meter_id', None)
            if meter_id:
                meter = get_object_or_404(Meter, device_id=meter_id)
                data_points = MeterData.objects.filter(meter=meter)
            else:
                data_points = MeterData.objects.all()

            serializer = MeterDataSerializer(data_points, many=True)
            return Response({
                "details": {
                    "message": "Meter data retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Get a specific meter data point by ID"""
        try:
            print(f"Attempting to retrieve meter data with pk={pk}")
            data = MeterData.objects.filter(meter=pk).first()
            print(f"Found data: {data}")
            # This will never execute since get_object_or_404 raises an exception if not found
            if not data:
                print("Data is None - this line should never be reached")
                return Response({
                    "error": "Meter data not found"
                }, status=status.HTTP_404_NOT_FOUND)
            print(f"Serializing data with id={data.id}")
            serializer = MeterDataSerializer(data)
            return Response({
                "details": {
                    "message": "Meter data retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except MeterData.DoesNotExist:
            print(f"MeterData with meter={pk} does not exist")
            return Response({
                "error": "Meter data not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return Response({
                "error": "Error retrieving meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Create a new meter data point from API payload"""
        try:
            # Extract meter_id from payload
            meter_id = request.data.get('meter_id')
            data = request.data.get('data', {})

            if not meter_id:
                return Response({
                    "error": "meter_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the meter
            try:
                meter = Meter.objects.get(device_id=meter_id)
            except Meter.DoesNotExist:
                return Response({
                    "error": f"Meter with device_id {meter_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Prepare data object
            meter_data = {
                'meter': meter.id,
                'engine_hours': data.get('engine_hours', 0),
                'frequency_hz': data.get('frequency_hz', 0),
                'power_percentage': data.get('power_percentage', 0),

                # Average readings
                'avg_ll_volt': data.get('avg_ll_volt', 0),
                'avg_ln_volt': data.get('avg_ln_volt', 0),
                'avg_current': data.get('avg_current', 0),

                # Phase A data
                'phase_a_voltage_v': data.get('phase_a', {}).get('voltage_v', 0),
                'phase_a_current_a': data.get('phase_a', {}).get('current_a', 0),
                'phase_a_voltage_ll': data.get('phase_a', {}).get('voltage_ll', 0),
                'phase_a_frequency_hz': data.get('phase_a', {}).get('frequency_hz', 0),
                'phase_a_real_power': data.get('phase_a', {}).get('real_power', 0),
                'phase_a_apparent_power': data.get('phase_a', {}).get('apparent_power', 0),
                'phase_a_reactive_power': data.get('phase_a', {}).get('reactive_power', 0),

                # Phase B data
                'phase_b_voltage_v': data.get('phase_b', {}).get('voltage_v', 0),
                'phase_b_current_a': data.get('phase_b', {}).get('current_a', 0),
                'phase_b_voltage_ll': data.get('phase_b', {}).get('voltage_ll', 0),
                'phase_b_frequency_hz': data.get('phase_b', {}).get('frequency_hz', 0),
                'phase_b_real_power': data.get('phase_b', {}).get('real_power', 0),
                'phase_b_apparent_power': data.get('phase_b', {}).get('apparent_power', 0),
                'phase_b_reactive_power': data.get('phase_b', {}).get('reactive_power', 0),

                # Phase C data
                'phase_c_voltage_v': data.get('phase_c', {}).get('voltage_v', 0),
                'phase_c_current_a': data.get('phase_c', {}).get('current_a', 0),
                'phase_c_voltage_ll': data.get('phase_c', {}).get('voltage_ll', 0),
                'phase_c_frequency_hz': data.get('phase_c', {}).get('frequency_hz', 0),
                'phase_c_real_power': data.get('phase_c', {}).get('real_power', 0),
                'phase_c_apparent_power': data.get('phase_c', {}).get('apparent_power', 0),
                'phase_c_reactive_power': data.get('phase_c', {}).get('reactive_power', 0),

                # Breaker statuses
                'gen_breaker': data.get('gen_breaker'),
                'util_breaker': data.get('util_breaker'),
                'gc_status': data.get('gc_status'),

                # Other measurements
                'coolant_temp_c': data.get('coolant_temp_c', 0),
                'oil_pressure_kpa': data.get('oil_pressure_kpa', 0),
                'battery_voltage_v': data.get('battery_voltage_v', 0),
                'fuel_level_percent': data.get('fuel_level_percent', 0),
                'rpm': data.get('rpm', 0),
                'oil_temp_c': data.get('oil_temp_c', 0),
                'boost_pressure_kpa': data.get('boost_pressure_kpa', 0),
                'intake_air_temp_c': data.get('intake_air_temp_c', 0),
                'fuel_rate_lph': data.get('fuel_rate_lph', 0),
                'instantaneous_power_kw': data.get('instantaneous_power_kw', 0),

                # Alarms
                'alarm_emergency_stop': data.get('alarms', {}).get('emergency_stop', False),
                'alarm_low_oil_pressure': data.get('alarms', {}).get('low_oil_pressure', False),
                'alarm_high_coolant_temp': data.get('alarms', {}).get('high_coolant_temp', False),
                'alarm_low_coolant_level': data.get('alarms', {}).get('low_coolant_level', False),
                'alarm_crank_failure': data.get('alarms', {}).get('crank_failure', False),
            }

            # Validate and save
            serializer = MeterDataSerializer(data=meter_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "details": {
                        "message": "Meter data recorded successfully",
                        "data": serializer.data
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": "Invalid data",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": "Error recording meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest data for each meter"""
        try:
            latest_data = {}
            for meter in Meter.objects.all():
                data = MeterData.objects.filter(meter=meter).order_by('-timestamp').first()
                if data:
                    latest_data[meter.device_id] = MeterDataSerializer(data).data

            return Response({
                "details": {
                    "message": "Latest meter data retrieved successfully",
                    "data": latest_data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving latest meter data",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GenerateAlarmReport(viewsets.ViewSet):
    def create(self, request):
        """
        Generate an alarm report for a specific meter and return a download URL.
        """
        try:
            meter_id = request.data.get('meter_id')

            if not meter_id:
                return Response({
                    "error": "meter_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the meter
            try:
                meter = Meter.objects.get(device_id=meter_id)
            except Meter.DoesNotExist:
                return Response({
                    "error": f"Meter with device_id {meter_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Get the most recent data point
            data = MeterData.objects.filter(meter=meter).order_by('-timestamp').first()

            if not data:
                return Response({
                    "error": "No data found for this meter"
                }, status=status.HTTP_404_NOT_FOUND)

            # Create Excel file with only the most recent data point
            report_data = {
                'Metric': [
                    'Timestamp',
                    'Emergency Stop',
                    'Low Oil Pressure',
                    'High Coolant Temp',
                    'Low Coolant Level',
                    'Crank Failure',
                    'Coolant Temp (°C)',
                    'Oil Pressure (kPa)',
                    'Engine Hours',
                    'Fuel Level (%)'
                ],
                'Current Value': [
                    data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Yes' if data.alarm_emergency_stop else 'No',
                    'Yes' if data.alarm_low_oil_pressure else 'No',
                    'Yes' if data.alarm_high_coolant_temp else 'No',
                    'Yes' if data.alarm_low_coolant_level else 'No',
                    'Yes' if data.alarm_crank_failure else 'No',
                    data.coolant_temp_c,
                    data.oil_pressure_kpa,
                    data.engine_hours,
                    data.fuel_level_percent
                ]
            }

            # Create DataFrame
            df = pd.DataFrame(report_data)

            # Create a buffer to save the Excel file
            buffer = BytesIO()

            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Alarm Report', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Alarm Report']

                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D7E4BC',
                    'border': 1
                })

                # Format the header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Format the metric names column
                metric_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#E6E6E6',
                    'border': 1
                })

                for row_num in range(df.shape[0]):
                    worksheet.write(row_num + 1, 0, df['Metric'][row_num], metric_format)

                # Set column widths
                worksheet.set_column(0, 0, 25)  # Metric names column
                worksheet.set_column(1, 1, 25)  # Values column

                # Add device info at the bottom
                info_format = workbook.add_format({
                    'bold': True,
                    'font_size': 12,
                    'font_color': 'blue'
                })
                worksheet.write(df.shape[0] + 3, 0, "Device ID:", info_format)
                worksheet.write(df.shape[0] + 3, 1, meter_id)
                worksheet.write(df.shape[0] + 4, 0, "Report Generated At:", info_format)
                worksheet.write(df.shape[0] + 4, 1, timezone.now().strftime('%Y-%m-%d %H:%M:%S'))

            # Save the Excel file
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alarm_report_{meter_id}_{timestamp}.xlsx"
            file_path = f"reports/{filename}"

            # Reset buffer position
            buffer.seek(0)

            # Save to storage
            default_storage.save(file_path, ContentFile(buffer.getvalue()))

            # Generate download URL
            download_url = request.build_absolute_uri(f'/media/{file_path}')

            return Response({
                "details": {
                    "message": "Alarm report generated successfully",
                    "filename": filename,
                    "download_url": download_url
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Error generating alarm report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Download a specific report by filename and delete it afterward
        """
        try:
            filename = pk
            file_path = f"reports/{filename}"

            if not default_storage.exists(file_path):
                return Response({
                    "error": "Report file not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Read the file
            file_content = default_storage.open(file_path).read()

            # Create HTTP response with file
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            # Delete the file after sending
            default_storage.delete(file_path)

            return response

        except Exception as e:
            return Response({
                "error": "Error downloading report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GenerateMeterReport(viewsets.ViewSet):
    def create(self, request):
        """
        Generate a comprehensive report with only the most recent meter data for a specific meter.
        """
        try:
            meter_id = request.data.get('meter_id')

            if not meter_id:
                return Response({
                    "error": "meter_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the meter
            try:
                meter = Meter.objects.get(device_id=meter_id)
            except Meter.DoesNotExist:
                return Response({
                    "error": f"Meter with device_id {meter_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Get only the most recent data point
            data = MeterData.objects.filter(meter=meter).order_by('-timestamp').first()

            if not data:
                return Response({
                    "error": "No data found for this meter"
                }, status=status.HTTP_404_NOT_FOUND)

            # Create a buffer to save the Excel file
            buffer = BytesIO()

            # Create DataFrame with a single column for the most recent data
            report_data = {
                'Metric': [
                    'Timestamp',
                    # Basic meter data
                    'Engine Hours',
                    'Frequency (Hz)',
                    'Power (%)',
                    # Average readings
                    'Avg Line-to-Line Voltage',
                    'Avg Line-to-Neutral Voltage',
                    'Avg Current',
                    # Phase A data
                    'Phase A Voltage (V)',
                    'Phase A Current (A)',
                    'Phase A Voltage Line-to-Line',
                    'Phase A Frequency (Hz)',
                    'Phase A Real Power',
                    'Phase A Apparent Power',
                    'Phase A Reactive Power',
                    # Phase B data
                    'Phase B Voltage (V)',
                    'Phase B Current (A)',
                    'Phase B Voltage Line-to-Line',
                    'Phase B Frequency (Hz)',
                    'Phase B Real Power',
                    'Phase B Apparent Power',
                    'Phase B Reactive Power',
                    # Phase C data
                    'Phase C Voltage (V)',
                    'Phase C Current (A)',
                    'Phase C Voltage Line-to-Line',
                    'Phase C Frequency (Hz)',
                    'Phase C Real Power',
                    'Phase C Apparent Power',
                    'Phase C Reactive Power',
                    # Breaker statuses
                    'Generator Breaker',
                    'Utility Breaker',
                    'GC Status',
                    # Temperature and pressure
                    'Coolant Temp (°C)',
                    'Oil Temp (°C)',
                    'Intake Air Temp (°C)',
                    'Oil Pressure (kPa)',
                    'Boost Pressure (kPa)',
                    # Fuel metrics
                    'Fuel Level (%)',
                    'Fuel Rate (L/h)',
                    # Others
                    'RPM',
                    'Battery Voltage (V)',
                    'Instantaneous Power (kW)',
                    # Alarms
                    'Emergency Stop',
                    'Low Oil Pressure',
                    'High Coolant Temp',
                    'Low Coolant Level',
                    'Crank Failure',
                ],
                'Current Value': [
                    data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    data.engine_hours,
                    data.frequency_hz,
                    data.power_percentage,
                    data.avg_ll_volt,
                    data.avg_ln_volt,
                    data.avg_current,
                    data.phase_a_voltage_v,
                    data.phase_a_current_a,
                    data.phase_a_voltage_ll,
                    data.phase_a_frequency_hz,
                    data.phase_a_real_power,
                    data.phase_a_apparent_power,
                    data.phase_a_reactive_power,
                    data.phase_b_voltage_v,
                    data.phase_b_current_a,
                    data.phase_b_voltage_ll,
                    data.phase_b_frequency_hz,
                    data.phase_b_real_power,
                    data.phase_b_apparent_power,
                    data.phase_b_reactive_power,
                    data.phase_c_voltage_v,
                    data.phase_c_current_a,
                    data.phase_c_voltage_ll,
                    data.phase_c_frequency_hz,
                    data.phase_c_real_power,
                    data.phase_c_apparent_power,
                    data.phase_c_reactive_power,
                    data.gen_breaker,
                    data.util_breaker,
                    data.gc_status,
                    data.coolant_temp_c,
                    data.oil_temp_c,
                    data.intake_air_temp_c,
                    data.oil_pressure_kpa,
                    data.boost_pressure_kpa,
                    data.fuel_level_percent,
                    data.fuel_rate_lph,
                    data.rpm,
                    data.battery_voltage_v,
                    data.instantaneous_power_kw,
                    'Yes' if data.alarm_emergency_stop else 'No',
                    'Yes' if data.alarm_low_oil_pressure else 'No',
                    'Yes' if data.alarm_high_coolant_temp else 'No',
                    'Yes' if data.alarm_low_coolant_level else 'No',
                    'Yes' if data.alarm_crank_failure else 'No',
                ]
            }

            # Create DataFrame
            df = pd.DataFrame(report_data)

            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Meter Data Report', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Meter Data Report']

                # Add some formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D7E4BC',
                    'border': 1
                })

                # Format the header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Format the metric names column
                metric_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#E6E6E6',
                    'border': 1
                })

                for row_num in range(df.shape[0]):
                    worksheet.write(row_num + 1, 0, df['Metric'][row_num], metric_format)

                # Set column widths
                worksheet.set_column(0, 0, 30)  # Metric names column
                worksheet.set_column(1, 1, 25)  # Values column

                # Add device info at the bottom
                info_format = workbook.add_format({
                    'bold': True,
                    'font_size': 12,
                    'font_color': 'blue'
                })
                worksheet.write(df.shape[0] + 3, 0, "Device ID:", info_format)
                worksheet.write(df.shape[0] + 3, 1, meter_id)
                worksheet.write(df.shape[0] + 4, 0, "Report Generated At:", info_format)
                worksheet.write(df.shape[0] + 4, 1, timezone.now().strftime('%Y-%m-%d %H:%M:%S'))

            # Save the Excel file
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"meter_data_report_{meter_id}_{timestamp}.xlsx"
            file_path = f"reports/{filename}"

            # Reset buffer position
            buffer.seek(0)

            # Save to storage
            default_storage.save(file_path, ContentFile(buffer.getvalue()))

            # Generate download URL
            download_url = request.build_absolute_uri(f'/media/{file_path}')

            return Response({
                "details": {
                    "message": "Meter data report generated successfully",
                    "filename": filename,
                    "download_url": download_url
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()

            return Response({
                "error": "Error generating meter data report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        Download a specific meter report by filename and delete it afterward
        """
        try:
            filename = pk
            file_path = f"reports/{filename}"

            if not default_storage.exists(file_path):
                return Response({
                    "error": "Report file not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Read the file
            file_content = default_storage.open(file_path).read()

            # Create HTTP response with file
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            # Delete the file after sending
            default_storage.delete(file_path)

            return response

        except Exception as e:
            return Response({
                "error": "Error downloading report",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
