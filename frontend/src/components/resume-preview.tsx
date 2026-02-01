'use client';

import React from 'react';
import clsx from 'clsx';

interface ResumePreviewProps {
    data: any;
}

export function ResumePreview({ data }: ResumePreviewProps) {
    const { content, template_id } = data;
    const { personal_info, experience, education, skills } = content || {};

    return (
        <div className="bg-white shadow-lg w-full h-full min-h-[800px] p-8 border border-gray-200">
            <div className="mb-8 border-b pb-4">
                <h1 className="text-3xl font-bold text-gray-900 uppercase tracking-wide">
                    {personal_info?.name || 'Your Name'}
                </h1>
                <div className="mt-2 text-sm text-gray-600 flex space-x-4">
                    {personal_info?.email && <span>{personal_info.email}</span>}
                    {personal_info?.phone && <span>| {personal_info.phone}</span>}
                </div>
            </div>

            {personal_info?.summary && (
                <div className="mb-6">
                    <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Summary</h2>
                    <p className="text-sm text-gray-800 leading-relaxed">{personal_info.summary}</p>
                </div>
            )}

            {/* Placeholders for other sections if array exists */}
            <div className="text-center text-gray-400 text-sm mt-10 italic">
                (Experience and Education sections will appear here when added)
            </div>

            {/* ATS Analysis Results */}
            {data.ats_score !== undefined && data.ats_score !== null && (
                <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-blue-800 uppercase tracking-wider">ATS Analysis</h2>
                        <div className="flex items-center">
                            <span className="text-sm text-blue-600 mr-2">Score:</span>
                            <span className={clsx(
                                "text-2xl font-bold",
                                data.ats_score >= 70 ? "text-green-600" : data.ats_score >= 40 ? "text-orange-500" : "text-red-500"
                            )}>{data.ats_score}/100</span>
                        </div>
                    </div>

                    {data.analysis_results && (
                        <div className="space-y-3 text-sm text-gray-700">
                            <p className="font-medium">{data.analysis_results.summary}</p>

                            {data.analysis_results.keywords_found && data.analysis_results.keywords_found.length > 0 && (
                                <div>
                                    <h3 className="font-semibold text-blue-700">Keywords Found:</h3>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {data.analysis_results.keywords_found.map((k: string, i: number) => (
                                            <span key={i} className="px-2 py-0.5 bg-green-100 text-green-800 rounded text-xs">{k}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {data.analysis_results.missing_keywords && data.analysis_results.missing_keywords.length > 0 && (
                                <div>
                                    <h3 className="font-semibold text-red-700">Missing Keywords:</h3>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {data.analysis_results.missing_keywords.map((k: string, i: number) => (
                                            <span key={i} className="px-2 py-0.5 bg-red-100 text-red-800 rounded text-xs">{k}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {data.analysis_results.feedback && data.analysis_results.feedback.length > 0 && (
                                <div>
                                    <h3 className="font-semibold text-orange-700">Feedback:</h3>
                                    <ul className="list-disc list-inside mt-1 space-y-1">
                                        {data.analysis_results.feedback.map((f: string, i: number) => (
                                            <li key={i}>{f}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Template Footer */}
            <div className="mt-auto pt-4 text-[10px] text-gray-300 text-center">
                Template: {template_id}
            </div>
        </div>
    );
}
